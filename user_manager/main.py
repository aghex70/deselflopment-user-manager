from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from persistence import crud, database, schemas, utils
from sqlalchemy.orm import Session


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create a FastAPI app instance
app = FastAPI()

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="templates")


# Define a simple API endpoint that renders a template
@app.get("/")
def root(request: Request):
    # Render the template with a custom message
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/register")
def read_register(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {"request": request},
    )


@app.post("/register", response_model=schemas.UserRegister)
def register(user: schemas.UserRegister, db: Session = Depends(get_db)):
    if not user.email:
        raise HTTPException(status_code=400, detail="Email is required")

    if not user.password:
        raise HTTPException(status_code=400, detail="Password is required")

    if not user.repeat_password:
        raise HTTPException(status_code=400, detail="Repeat password is required")

    if not user.password == user.repeat_password:
        raise HTTPException(status_code=400, detail="Passwords don't match")

    if not user.name:
        raise HTTPException(status_code=400, detail="Name is required")

    if crud.get_user_by_email(db, email=user.email):
        raise HTTPException(status_code=400, detail="User already registered")

    if db_user := crud.create_user(db=db, user=user):
        subject, body = utils.generate_welcome_email(db_user)
        email_sent, error = utils.send_email(subject, body, db_user.email)
        crud.create_email(db, subject, body, db_user.id, "register", email_sent, error)
        if not email_sent:
            raise HTTPException(status_code=400, detail=error)
        return Response(status_code=201)


@app.get("/activate/{activation_code}")
def activate(request: Request, activation_code: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_activation_code(db, activation_code)
    if not db_user:
        return RedirectResponse(url="/login")

    crud.activate_user(db, db_user)

    return templates.TemplateResponse(
        "login.html", {"request": request, "message": "Proceed to login!"}
    )


@app.get("/login")
def read_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_model=schemas.UserLoginResponse)
def login(user: schemas.UserBase, db: Session = Depends(get_db)):
    db_user, error = crud.get_user(db, email=user.email, password=user.password)
    if error:
        raise HTTPException(status_code=400, detail=error)

    token = utils.generate_jwt_token(db_user)
    return schemas.UserLoginResponse(access_token=token, user_id=db_user.id)


@app.post("/refresh-token", response_model=schemas.UserLoginResponse)
def refresh_token(user: schemas.UserRefreshToken, db: Session = Depends(get_db)):
    user_id, error = utils.retrieve_jwt_claims(user)
    if error:
        raise HTTPException(status_code=401, detail=error)

    db_user = crud.get_user_by_id(db, user_id)
    token = utils.generate_jwt_token(db_user)
    return schemas.UserLoginResponse(access_token=token, user_id=db_user.id)


@app.get("/reset-link")
def read_reset_link(request: Request):
    return templates.TemplateResponse("reset_link.html", {"request": request})


@app.post(
    "/reset-link",
)
def reset_link(user: schemas.UserResetLink, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email")

    subject, body = utils.generate_password_reset_email(db_user)
    email_sent, error = utils.send_email(subject, body, db_user.email)
    crud.create_email(
        db, subject, body, db_user.id, "reset_password_link", email_sent, error
    )
    if not email_sent:
        raise HTTPException(status_code=400, detail=error)
    return Response(status_code=200)


@app.get("/reset-password/{reset_password_code}")
def read_reset_password(
    request: Request, reset_password_code: str, db: Session = Depends(get_db)
):
    db_user = crud.get_user_by_reset_password_code(db, reset_password_code)
    if not db_user:
        return RedirectResponse(url="/reset-link")

    return templates.TemplateResponse("reset_password.html", {"request": request})


@app.post("/reset-password")
def reset_password(user: schemas.UserResetPassword, db: Session = Depends(get_db)):
    if user.password != user.repeat_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    db_user = crud.get_user_by_reset_password_code(db, user.reset_password_code)
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid reset code")

    crud.update_user_password(db, db_user, user.password)
    return Response(status_code=200)


@app.get("/home")
def root(request: Request):
    # Render the template with a custom message
    return templates.TemplateResponse("home.html", {"request": request})
