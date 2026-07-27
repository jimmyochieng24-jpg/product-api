from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import field_validator
import re


class SupplierBase(SQLModel):
    name: str = Field(unique=True)
    contact_person: str
    email: str = Field(unique=True)
    phone: str
    is_active: bool = True

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(pattern, value):
            raise ValueError("Invalid email format")
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):
        pattern = r"^\+?[0-9]{10,15}$"
        if not re.match(pattern, value):
            raise ValueError("Invalid phone number")
        return value


class Supplier(SupplierBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class SupplierCreate(SupplierBase):
    pass