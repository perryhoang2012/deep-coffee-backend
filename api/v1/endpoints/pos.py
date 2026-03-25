from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from models.pos import Category, Product, Invoice, InvoiceItem, Payment, Table
from schemas.pos import (
    CategoryCreate, CategoryUpdate, CategoryResponse, 
    ProductCreate, ProductUpdate, ProductResponse, 
    InvoiceCreate, InvoiceResponse,
    TableCreate, TableUpdate, TableResponse
)
from api.dependencies import get_current_active_user
from models.admin import User
from datetime import datetime

router = APIRouter()

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

@router.get("/products", response_model=List[ProductResponse])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Product).offset(skip).limit(limit).all()

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

    # Create Items
    for item in invoice_in.items:
        db_item = InvoiceItem(
            invoice_id=db_invoice.id,
            **item.model_dump()
        )
        db.add(db_item)
        
    # Create Payments
    for pmt in invoice_in.payments:
        db_pmt = Payment(
            invoice_id=db_invoice.id,
            paid_at=datetime.utcnow(),
            **pmt.model_dump()
        )
        db.add(db_pmt)

    db.commit()
    db.refresh(db_invoice)
    return db_invoice

@router.get("/invoices", response_model=List[InvoiceResponse])
def read_invoices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Invoice).offset(skip).limit(limit).all()

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
