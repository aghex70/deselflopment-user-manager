from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from persistence import crud, database, utils, schemas


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
    return templates.TemplateResponse(
        "index.html", {"request": request, "message": "Hello to my website!"}
    )


@app.get("/register")
def read_register(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {"request": request, "message": "Hello to my register template!"},
    )


@app.post("/register", response_model=schemas.UserRegister)
def register(user: schemas.UserRegister, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")

    if crud.create_user(db=db, user=user):
        return templates.TemplateResponse(
            "login.html", {"request": {}, "message": "lol"}
        )


@app.get("/login")
def read_login(request: Request):
    return templates.TemplateResponse(
        "login.html", {"request": request, "message": "Hello to my login template!"}
    )


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

    # http.HandleFunc("/api/reset-link", s.userHandler.ResetLink)
    # http.HandleFunc("/api/reset-password", s.userHandler.ResetPassword)
    # http.HandleFunc("/api/users", JWTAuthMiddleware(s.userHandler.ListUsers))
    # http.HandleFunc("/api/user/admin", JWTAuthMiddleware(s.userHandler.CheckAdmin))
    # http.HandleFunc("/api/user/provision", JWTAuthMiddleware(s.userHandler.ProvisionDemoUser))
    # http.HandleFunc("/api/user/activate", s.userHandler.ActivateUser)
