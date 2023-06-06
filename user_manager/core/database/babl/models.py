from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Table,
)
from sqlalchemy.orm import Session

from core.database import metadata
from core.utils.common import generate_uuid

if TYPE_CHECKING:
    from core.database.models import User

babl_users_table = Table(
    "babl_users",
    metadata,
    Column("id", String, primary_key=True),
    Column("name", String),
    Column("email", String),
    Column("admin", Boolean),
    Column("password", String),
    Column("activation_code", String),
    Column("active", Boolean),
    Column("reset_password_code", String),
    extend_existing=True,
)

def create_babl_user(db: Session, user: "User"):
    babl_users_insert = babl_users_table.insert().values(
        id=generate_uuid(),
        active=False,
        admin=False,
        name=user.name,
        email=user.email,
        password=user.password,
        activation_code=user.activation_code,
        reset_password_code=user.reset_password_code,
    )
    db.execute(babl_users_insert)



