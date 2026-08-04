from typing import Optional
from sqlmodel import SQLModel, Field


class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    role: str = "user"


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str


class UserCreate(SQLModel):
    username: str
    email: str
    password: str
    role: str = "user"


class UserLogin(SQLModel):
    username: str
    password: str