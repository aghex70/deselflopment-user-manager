import logging
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from ..schemas import auth
from ..utils.auth import decrypt_password, encrypt_password
from ..utils.common import generate_uuid

logger = logging.getLogger(__name__)
Base = declarative_base()

class User(Base):
    __tablename__ = "deselflopment_users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128))
    email = Column(String(128), unique=True, index=True)
    admin = Column(Boolean, default=False)
    registration_date = Column(DateTime, default=datetime.utcnow)
    password = Column(String(128))
    activation_code = Column(String(50), unique=True, index=True)
    active = Column(Boolean, default=False)
    reset_password_code = Column(String(50), unique=True, index=True)

    @classmethod
    def create(
        cls, db: Session, user_schema: auth.UserRegister
    ) -> "User":
        encrypted_password = encrypt_password(user_schema.password)
        user = cls(
            name=user_schema.name,
            email=user_schema.email,
            password=encrypted_password,
            activation_code=generate_uuid(),
            reset_password_code=generate_uuid(),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @classmethod
    def get_by_email(cls, db: Session, email: str) -> "User":
        return db.query(cls).filter(cls.email == email).first()

    @classmethod
    def get_by_email_and_password(
        cls, db: Session, email: str, password: str
    ) -> tuple["User", str] | tuple[None, str]:
        user = cls.get_by_email(db, email)
        if not user:
            return None, "User not registered"

        if not user.active:
            return None, "User not active"

        decrypted_password = decrypt_password(user.password)
        if decrypted_password != password:
            return None, "Invalid password"

        return user, ""

    @classmethod
    def get_by_activation_code(cls, db: Session, activation_code: str) -> "User":
        return db.query(cls).filter(cls.activation_code == activation_code).first()

    @classmethod
    def get_by_reset_password_code(
        cls, db: Session, reset_password_code: str
    ) -> "User":
        return (
            db.query(cls).filter(cls.reset_password_code == reset_password_code).first()
        )

    @classmethod
    def get_by_id(cls, db: Session, user_id: int) -> "User":
        return db.query(cls).filter(cls.id == user_id).first()

    def activate(self, db: Session) -> None:
        if self.active:
            logger.warning(f"User {self.email} already active")

        self.active = True
        db.commit()
        db.refresh(self)

    def update_password(self, db: Session, password: str) -> None:
        encrypted_password = encrypt_password(password)
        self.password = encrypted_password
        self.reset_password_code = generate_uuid()
        db.commit()
        db.refresh(self)


class Email(Base):
    __tablename__ = "deselflopment_emails"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(128), default="deselflopment")
    subject = Column(String(128))
    body = Column(Text())
    creation_date = Column(DateTime, default=datetime.utcnow)
    sent = Column(Boolean, default=False)
    error = Column(Text(), nullable=True)
    user_id = Column(Integer, ForeignKey("deselflopment_users.id"))

    @classmethod
    def create(
        cls,
        db: Session,
        subject: str,
        body: str,
        user_id: int,
        source: str,
        sent: bool,
        error: None,
    ) -> "Email":
        email = cls(
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
