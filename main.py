from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from datetime import datetime
from sqlmodel import Session, select
from typing import List

from database.session import get_session, create_db_and_tables
from models.product import (
    Product,
    ProductCreate,
    ProductUpdate,
    BulkPriceUpdate,
    StockAdjustment,
)
from models.supplier import (
    Supplier,
    SupplierCreate,
)

app = FastAPI(
    title="Product Inventory API",
    version="1.0.0"
)
# ==========================
# ERROR RESPONSE HANDLERS
# ==========================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "status_code": exc.status_code,
            "message": exc.detail,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path),
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "status_code": 422,
            "message": "Validation Error",
            "errors": exc.errors(),
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "status_code": 500,
            "message": "Internal Server Error",
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path),
        },
    )


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def root():
    return {"message": "Welcome to Product Inventory API"}


# ==========================
# SUPPLIER ENDPOINTS
# ==========================

@app.post("/suppliers", response_model=Supplier, status_code=201)
def create_supplier(
    supplier: SupplierCreate,
    session: Session = Depends(get_session)
):
    db_supplier = Supplier(**supplier.model_dump())
    session.add(db_supplier)
    session.commit()
    session.refresh(db_supplier)
    return db_supplier


@app.get("/suppliers", response_model=List[Supplier])
def list_suppliers(session: Session = Depends(get_session)):
    return session.exec(select(Supplier)).all()


@app.get("/suppliers/{supplier_id}", response_model=Supplier)
def get_supplier(
    supplier_id: int,
    session: Session = Depends(get_session)
):
    supplier = session.get(Supplier, supplier_id)

    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    return supplier


# ==========================
# PRODUCT ENDPOINTS
# ==========================

@app.post("/products", response_model=Product, status_code=201)
def create_product(
    product: ProductCreate,
    session: Session = Depends(get_session)
):
    if product.supplier_id is not None:
        supplier = session.get(Supplier, product.supplier_id)

        if not supplier:
            raise HTTPException(
                status_code=404,
                detail="Supplier not found"
            )

    db_product = Product(**product.model_dump())

    session.add(db_product)
    session.commit()
    session.refresh(db_product)

    return db_product


@app.get("/products", response_model=List[Product])
def list_products(session: Session = Depends(get_session)):
    return session.exec(select(Product)).all()


# ==========================
# BULK PRICE UPDATE
# ==========================

@app.patch("/products/bulk-update")
def bulk_update_price(
    request: BulkPriceUpdate,
    session: Session = Depends(get_session)
):
    products = session.exec(
        select(Product).where(Product.category == request.category)
    ).all()

    if not products:
        raise HTTPException(
            status_code=404,
            detail="No products found in this category"
        )

    updated_count = 0

    for product in products:
        new_price = product.price * (1 - request.discount_percent / 100)

        if new_price < 100:
            continue

        product.price = new_price
        session.add(product)
        updated_count += 1

    session.commit()

    return {
        "message": "Bulk update completed",
        "category": request.category,
        "discount_percent": request.discount_percent,
        "products_updated": updated_count
    }


# ==========================
# STOCK ADJUSTMENT
# ==========================

@app.patch("/products/adjust-stock")
def adjust_stock(
    adjustments: List[StockAdjustment],
    session: Session = Depends(get_session)
):
    successful_updates = []
    failed_updates = []

    for adjustment in adjustments:

        product = session.get(Product, adjustment.product_id)

        # Check product exists
        if not product:
            failed_updates.append({
                "product_id": adjustment.product_id,
                "reason": "Product not found"
            })
            continue

        # Calculate new stock
        new_quantity = product.quantity + adjustment.quantity_to_add

        # Validate maximum stock
        if new_quantity > 5000:
            failed_updates.append({
                "product_id": adjustment.product_id,
                "reason": "Stock cannot exceed 5000 units"
            })
            continue

        # Update stock
        product.quantity = new_quantity
        session.add(product)

        successful_updates.append({
            "product_id": product.id,
            "new_quantity": product.quantity
        })

    session.commit()

    return {
        "successful_updates": successful_updates,
        "failed_updates": failed_updates
    }


# ==========================
# SINGLE PRODUCT
# ==========================

@app.get("/products/{product_id}", response_model=Product)
def get_product(
    product_id: int,
    session: Session = Depends(get_session)
):
    product = session.get(Product, product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@app.patch("/products/{product_id}", response_model=Product)
def update_product(
    product_id: int,
    updated_product: ProductUpdate,
    session: Session = Depends(get_session),
):
    product = session.get(Product, product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if updated_product.supplier_id is not None:
        supplier = session.get(Supplier, updated_product.supplier_id)

        if not supplier:
            raise HTTPException(
                status_code=404,
                detail="Supplier not found"
            )

    product.name = updated_product.name
    product.description = updated_product.description
    product.price = updated_product.price
    product.quantity = updated_product.quantity
    product.category = updated_product.category
    product.supplier_id = updated_product.supplier_id

    session.add(product)
    session.commit()
    session.refresh(product)

    return product


@app.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    session: Session = Depends(get_session)
):
    product = session.get(Product, product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    session.delete(product)
    session.commit()

    return {"message": "Product deleted successfully"}