from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text

from .database import Base


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
