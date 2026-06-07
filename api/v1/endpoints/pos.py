from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import String, asc, cast, desc, or_
from sqlalchemy.orm import Session
from core.database import get_db
from core.pagination import paginate_query
from models.pos import Category, Product, Invoice, InvoiceItem, Payment, Table
from schemas.pos import (
    CategoryCreate, CategoryUpdate, CategoryResponse, 
    ProductCreate, ProductUpdate, ProductResponse, 
    InvoiceCreate, InvoiceResponse,
    TableCreate, TableUpdate, TableResponse
)
from schemas.base import PaginatedResponse
from api.dependencies import get_current_active_user
from models.admin import User
from datetime import datetime

router = APIRouter()

PRODUCT_SORT_FIELDS = {
    "id": Product.id,
    "name": Product.name,
    "sku": Product.sku,
    "price": Product.price,
    "status": Product.status,
    "created_at": Product.created_at,
    "updated_at": Product.updated_at,
}

INVOICE_SORT_FIELDS = {
    "id": Invoice.id,
    "invoice_code": Invoice.invoice_code,
    "total_amount": Invoice.total_amount,
    "payment_status": Invoice.payment_status,
    "invoice_status": Invoice.invoice_status,
    "issued_at": Invoice.issued_at,
    "created_at": Invoice.created_at,
    "updated_at": Invoice.updated_at,
}

# --- Categories ---
@router.post("/categories", response_model=CategoryResponse)
def create_category(category_in: CategoryCreate, db: Session = Depends(get_db)):
    db_category = Category(**category_in.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/categories", response_model=List[CategoryResponse])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Category).offset(skip).limit(limit).all()

@router.get("/categories/{category_id}", response_model=CategoryResponse)
def read_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.put("/categories/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, category_in: CategoryUpdate, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    update_data = category_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
        
    db.commit()
    db.refresh(category)
    return category

@router.delete("/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
    return {"detail": "Category deleted successfully"}

# --- Products ---
@router.post("/products", response_model=ProductResponse)
def create_product(product_in: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(**product_in.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/products", response_model=PaginatedResponse[ProductResponse])
def read_products(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    skip: int | None = Query(default=None, ge=0),
    search: str | None = Query(default=None),
    status: str | None = Query(default=None),
    sort_by: str = Query(default="id"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
):
    products_query = db.query(Product)

    if search:
        search_term = f"%{search.strip()}%"
        products_query = products_query.filter(
            or_(
                Product.name.ilike(search_term),
                Product.sku.ilike(search_term),
            )
        )

    if status:
        products_query = products_query.filter(Product.status == status)

    sort_column = PRODUCT_SORT_FIELDS.get(sort_by, Product.id)
    sort_expression = asc(sort_column) if sort_order == "asc" else desc(sort_column)
    products_query = products_query.order_by(sort_expression)

    return paginate_query(products_query, page=page, limit=limit, skip=skip)

@router.get("/products/{product_id}", response_model=ProductResponse)
def read_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product_in: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
        
    db.commit()
    db.refresh(product)
    return product

@router.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"detail": "Product deleted successfully"}

# --- Invoices ---
@router.post("/invoices", response_model=InvoiceResponse)
def create_invoice(
    invoice_in: InvoiceCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    import uuid
    # Create main invoice
    db_invoice = Invoice(
        customer_id=invoice_in.customer_id,
        table_id=invoice_in.table_id,
        invoice_code=f"INV-{uuid.uuid4().hex[:8].upper()}",
        subtotal=invoice_in.subtotal,
        discount_amount=invoice_in.discount_amount,
        surcharge_amount=invoice_in.surcharge_amount,
        total_amount=invoice_in.total_amount,
        payment_status=invoice_in.payment_status,
        invoice_status=invoice_in.invoice_status,
        created_by=current_user.id,
        issued_at=datetime.utcnow()
    )
    db.add(db_invoice)
    db.flush() # get ID

    # Create Items and deduct stock
    for item in invoice_in.items:
        db_item = InvoiceItem(
            invoice_id=db_invoice.id,
            **item.model_dump()
        )
        db.add(db_item)
        
        # Deduct stock_quantity from Product
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            product.stock_quantity = max(0, product.stock_quantity - item.quantity)
        
    # Create Payments
    for pmt in invoice_in.payments:
        db_pmt = Payment(
            invoice_id=db_invoice.id,
            paid_at=datetime.utcnow(),
            **pmt.model_dump()
        )
        db.add(db_pmt)

    # Release Table status if table_id is provided and payment_status is paid
    if invoice_in.table_id and invoice_in.payment_status == "paid":
        table = db.query(Table).filter(Table.id == invoice_in.table_id).first()
        if table:
            table.status = "available"

    db.commit()
    db.refresh(db_invoice)
    return db_invoice

@router.get("/invoices", response_model=PaginatedResponse[InvoiceResponse])
def read_invoices(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    skip: int | None = Query(default=None, ge=0),
    search: str | None = Query(default=None),
    status: str | None = Query(default=None),
    sort_by: str = Query(default="id"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
):
    invoices_query = db.query(Invoice)

    if search:
        search_term = f"%{search.strip()}%"
        invoices_query = invoices_query.filter(
            or_(
                Invoice.invoice_code.ilike(search_term),
                cast(Invoice.id, String).ilike(search_term),
            )
        )

    if status:
        invoices_query = invoices_query.filter(Invoice.invoice_status == status)

    sort_column = INVOICE_SORT_FIELDS.get(sort_by, Invoice.id)
    sort_expression = asc(sort_column) if sort_order == "asc" else desc(sort_column)
    invoices_query = invoices_query.order_by(sort_expression)

    return paginate_query(invoices_query, page=page, limit=limit, skip=skip)

@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
def read_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@router.delete("/invoices/{invoice_id}")
def delete_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    db.delete(invoice)
    db.commit()
    return {"detail": "Invoice deleted successfully"}

# --- Tables ---
@router.post("/tables", response_model=TableResponse)
def create_table(table_in: TableCreate, db: Session = Depends(get_db)):
    db_table = Table(**table_in.model_dump())
    db.add(db_table)
    db.commit()
    db.refresh(db_table)
    return db_table

@router.get("/tables", response_model=List[TableResponse])
def read_tables(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Table).offset(skip).limit(limit).all()

@router.get("/tables/{table_id}", response_model=TableResponse)
def read_table(table_id: int, db: Session = Depends(get_db)):
    table = db.query(Table).filter(Table.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    return table

@router.put("/tables/{table_id}", response_model=TableResponse)
def update_table(table_id: int, table_in: TableUpdate, db: Session = Depends(get_db)):
    table = db.query(Table).filter(Table.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    
    update_data = table_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(table, field, value)
        
    db.commit()
    db.refresh(table)
    return table

@router.delete("/tables/{table_id}")
def delete_table(table_id: int, db: Session = Depends(get_db)):
    table = db.query(Table).filter(Table.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    db.delete(table)
    db.commit()
    return {"detail": "Table deleted successfully"}
