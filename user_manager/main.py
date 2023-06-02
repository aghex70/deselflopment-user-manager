import logging

from core.database import SessionLocal
from core.database.models import Email, User
from core.schemas import auth
from core.utils.auth import generate_jwt_token, retrieve_jwt_claims, retrieve_user_id
from core.utils.email import (
    generate_password_reset_email,
    generate_welcome_email,
    send_email,
)
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="core/templates")
app = FastAPI()


@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/register")
def read_register(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {"request": request},
    )


@app.post("/register", response_model=auth.UserRegister)
def register(user_schema: auth.UserRegister, db: Session = Depends(get_db)):
    if not user_schema.name:
        error = "Name is required"
        logger.error(error)
        raise HTTPException(status_code=400, detail=error)

    if not user_schema.email:
        error = "Email is required"
        logger.error(error)
        raise HTTPException(status_code=400, detail=error)

    if not user_schema.password:
        error = "Password is required"
        logger.error(error)
        raise HTTPException(status_code=400, detail=error)

    if not user_schema.repeat_password:
        error = "Repeat password is required"
        logger.error(error)
        raise HTTPException(status_code=400, detail=error)

    if not user_schema.password == user_schema.repeat_password:
        error = "Passwords do not match"
        logger.error(error)
        raise HTTPException(status_code=400, detail=error)

    if User.get_by_email(db=db, email=user_schema.email):
        error = "User already registered. Try with a different email"
        logger.error(error)
        raise HTTPException(status_code=400, detail=error)

    if user := User.create(db=db, user_schema=user_schema):
        subject, body = generate_welcome_email(user)
        email_sent, error = send_email(subject, body, user.email)
        Email.create(db, subject, body, user.id, "register", email_sent, error)
        if not email_sent:
            error = "Error sending welcome email"
            logger.error(error)
            raise HTTPException(status_code=400, detail=error)
        return Response(status_code=201)


@app.get("/activate/{activation_code}")
def activate(request: Request, activation_code: str, db: Session = Depends(get_db)):
    user = User.get_by_activation_code(db=db, activation_code=activation_code)
    if not user:
        return RedirectResponse(url="/login")

    user.activate(db)

    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/login")
def read_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_model=auth.UserLoginResponse)
def login(user: auth.UserBase, db: Session = Depends(get_db)):
    user, error = User.get_by_email_and_password(
        db=db, email=user.email, password=user.password
    )
    if error:
        logger.error(error)
        raise HTTPException(status_code=400, detail=error)

    token = generate_jwt_token(user)
    return auth.UserLoginResponse(access_token=token, user_id=user.id)


@app.post("/refresh-token", response_model=auth.UserLoginResponse)
def refresh_token(user: auth.UserRefreshToken, db: Session = Depends(get_db)):
    token, error = retrieve_jwt_claims(user)
    if error:
        raise HTTPException(status_code=401, detail=error)

    user_id = retrieve_user_id(token=token)
    user = User.get_by_id(db=db, user_id=user_id)
    token = generate_jwt_token(user)
    return auth.UserLoginResponse(access_token=token, user_id=user_id)


@app.get("/reset-link")
def read_reset_link(request: Request):
    return templates.TemplateResponse("reset_link.html", {"request": request})


@app.post(
    "/reset-link",
)
def reset_link(user: auth.UserResetLink, db: Session = Depends(get_db)):
    user = User.get_by_email(db=db, email=user.email)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email")

    subject, body = generate_password_reset_email(user)
    email_sent, error = send_email(subject, body, user.email)
    Email.create(db, subject, body, user.id, "reset_password_link", email_sent, error)
    if not email_sent:
        raise HTTPException(status_code=400, detail=error)
    return Response(status_code=200)


@app.get("/reset-password/{reset_password_code}")
def read_reset_password(
    request: Request, reset_password_code: str, db: Session = Depends(get_db)
):
    user = User.get_by_reset_password_code(
        db=db, reset_password_code=reset_password_code
    )
    if not user:
        return RedirectResponse(url="/reset-link")

    return templates.TemplateResponse("reset_password.html", {"request": request})


@app.post("/reset-password")
def reset_password(user: auth.UserResetPassword, db: Session = Depends(get_db)):
    if user.password != user.repeat_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    user = User.get_by_reset_password_code(
        db=db, reset_password_code=user.reset_password_code
    )
    if not user:
        raise HTTPException(status_code=400, detail="Invalid reset code")

    user.update_password(db=db, password=user.password)
    return Response(status_code=200)


@app.get("/home")
def root(request: Request):
    # Render the template with a custom message
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/desync")
def desync(request: Request):
    return templates.TemplateResponse("desync.html", {"request": request})
