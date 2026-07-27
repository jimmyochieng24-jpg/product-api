from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from pydantic import field_validator


class ProductBase(SQLModel):
    name: str = Field(index=True)
    description: str
    price: float
    quantity: int
    category: str = Field(index=True)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if len(value.strip()) < 3:
            raise ValueError("Product name must be at least 3 characters long")
        return value

    @field_validator("price")
    @classmethod
    def validate_price(cls, value):
        if value <= 0:
            raise ValueError("Price must be greater than 0")
        return value

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, value):
        if value < 0:
            raise ValueError("Quantity cannot be negative")
        return value

    @field_validator("category")
    @classmethod
    def validate_category(cls, value):
        if value.strip() == "":
            raise ValueError("Category cannot be empty")
        return value


class Product(ProductBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    supplier_id: Optional[int] = Field(default=None, foreign_key="supplier.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ProductCreate(ProductBase):
    supplier_id: Optional[int] = None


class ProductUpdate(ProductBase):
    supplier_id: Optional[int] = None


class BulkPriceUpdate(SQLModel):
    category: str
    discount_percent: float = Field(gt=0, le=100)


class StockAdjustment(SQLModel):
    product_id: int
    quantity_to_add: int = Field(gt=0)