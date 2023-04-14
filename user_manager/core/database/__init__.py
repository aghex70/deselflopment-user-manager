from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..settings import DB_HOST, DB_NAME, DB_NETWORK, DB_PASSWORD, DB_PORT, DB_USER

user, password, network, host, port, name = (
    DB_USER,
    DB_PASSWORD,
    DB_NETWORK,
    DB_HOST,
    DB_PORT,
    DB_NAME,
)

SQLALCHEMY_DATABASE_URL = f"mysql://{user}:{password}@{host}:{port}/{name}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
