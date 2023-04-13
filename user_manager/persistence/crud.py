import logging

from sqlalchemy.orm import Session

from . import models, schemas, utils

logger = logging.getLogger(__name__)


def create_user(db: Session, user: schemas.UserRegister):
    encrypted_password = utils.encrypt_password(user.password)
    db_user = models.User(
        name=user.name,
        email=user.email,
        password=encrypted_password,
        activation_code=utils.generate_uuid(),
        reset_password_code=utils.generate_uuid(),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, email: str, password: str):
    db_user = get_user_by_email(db, email)
    if not db_user:
        return None, "User not registered"

    if not db_user.active:
        return None, "User not active"

    decrypted_password = utils.decrypt_password(db_user.password)
    if decrypted_password != password:
        return None, "Invalid password"

    return db_user, None


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


# def delete_user(db: Session, user: schemas.UserCreate):
#     db_user = models.User(email=user.email, hashed_password=user.password)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user


def create_email(
    db: Session,
    subject: str,
    body: str,
    user_id: int,
    source: str,
    sent: bool,
    error: None,
):
    email = models.Email(
        source=source,
        subject=subject,
        body=body,
        sent=sent,
        error=error,
        user_id=user_id,
    )
    db.add(email)
    db.commit()
    db.refresh(email)
    return email


def get_user_by_activation_code(db: Session, activation_code: str):
    return (
        db.query(models.User)
        .filter(models.User.activation_code == activation_code)
        .first()
    )


def activate_user(db: Session, user: models.User):
    if user.active:
        logger.warning(f"User {user.email} already active")

    user.active = True
    db.commit()
    db.refresh(user)


def get_user_by_reset_password_code(db: Session, reset_password_code: str):
    return (
        db.query(models.User)
        .filter(models.User.reset_password_code == reset_password_code)
        .first()
    )


def update_user_password(db: Session, user: models.User, password: str):
    encrypted_password = utils.encrypt_password(password)
    user.password = encrypted_password
    user.reset_password_code = utils.generate_uuid()
    db.commit()
    db.refresh(user)
