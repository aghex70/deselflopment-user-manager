from sqlalchemy.orm import Session

from . import utils, models, schemas


def create_user(db: Session, user: schemas.UserRegister):
    encrypted_password = utils.encrypt_password(user.password)
    db_user = models.User(
        name=user.name,
        email=user.email,
        password=encrypted_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, email: str, password: str):
    db_user = get_user_by_email(db, email)
    if not db_user:
        return None, "User not found"

    if not db_user.active:
        return None, "User not active"

    decrypted_password = utils.decrypt_password(db_user.password)
    if decrypted_password != password:
        return None, "Invalid credentials"

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
