from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from models.base import BaseModel

class Category(BaseModel):
    __tablename__ = "categories"
    
    name = Column(String, nullable=False)
    status = Column(String, default="active")
    sort_order = Column(Integer, default=0)

    products = relationship("Product", back_populates="category")

class Product(BaseModel):
    __tablename__ = "products"
    
    category_id = Column(Integer, ForeignKey("categories.id"))
    sku = Column(String, unique=True, index=True, nullable=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    status = Column(String, default="active")
    image_url = Column(String, nullable=True)

    category = relationship("Category", back_populates="products")

class Table(BaseModel):
    __tablename__ = "tables"
    
    name = Column(String, nullable=False)
    area = Column(String, nullable=True)
    status = Column(String, default="available") # available, occupied, reserved
    capacity = Column(Integer, nullable=True)

class Order(BaseModel):
    __tablename__ = "orders"
    
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True) # Will create customers table later
    order_status = Column(String, default="pending") # pending, processing, completed, cancelled
    created_by = Column(Integer, ForeignKey("users.id")) # from admin

class Invoice(BaseModel):
    __tablename__ = "invoices"
    
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    invoice_code = Column(String, unique=True, index=True, nullable=False)
    subtotal = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    surcharge_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    payment_status = Column(String, default="unpaid") # unpaid, paid, refunded
    invoice_status = Column(String, default="valid") # valid, cancelled, void
    created_by = Column(Integer, ForeignKey("users.id"))
    issued_at = Column(DateTime, nullable=True)

    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")

class InvoiceItem(BaseModel):
    __tablename__ = "invoice_items"
    
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    product_name_snapshot = Column(String, nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, default=0.0)
    line_total = Column(Float, default=0.0)
    note = Column(String, nullable=True)

    invoice = relationship("Invoice", back_populates="items")

class Payment(BaseModel):
    __tablename__ = "payments"
    
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    method = Column(String, nullable=False) # cash, credit_card, transfer
    amount = Column(Float, nullable=False)
    paid_at = Column(DateTime, nullable=False)
    reference_code = Column(String, nullable=True)

    invoice = relationship("Invoice", back_populates="payments")
