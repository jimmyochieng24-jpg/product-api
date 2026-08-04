from sqlmodel import SQLModel, Session, create_engine
from dotenv import load_dotenv
import os

# Import models so SQLModel creates their tables
from models.product import Product
from models.supplier import Supplier
from models.user import User

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session