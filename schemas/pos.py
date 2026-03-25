from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from schemas.base import BaseSchema

# Category
class CategoryBase(BaseModel):
    name: str
    status: Optional[str] = "active"
    sort_order: Optional[int] = 0

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    sort_order: Optional[int] = None

class CategoryResponse(CategoryBase, BaseSchema):
    pass

# Product
class ProductBase(BaseModel):
    category_id: int
    sku: Optional[str] = None
    name: str
    price: float
    status: Optional[str] = "active"
    image_url: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    category_id: Optional[int] = None
    sku: Optional[str] = None
    name: Optional[str] = None
    price: Optional[float] = None
    status: Optional[str] = None
    image_url: Optional[str] = None

class ProductResponse(ProductBase, BaseSchema):
    pass

# Table
class TableBase(BaseModel):
    name: str
    area: Optional[str] = None
    status: Optional[str] = "available"
    capacity: Optional[int] = None

class TableCreate(TableBase):
    pass

class TableUpdate(BaseModel):
    name: Optional[str] = None
    area: Optional[str] = None
    status: Optional[str] = None
    capacity: Optional[int] = None

class TableResponse(TableBase, BaseSchema):
    pass

# Order
class OrderBase(BaseModel):
    table_id: Optional[int] = None
    customer_id: Optional[int] = None
    order_status: Optional[str] = "pending"
    created_by: int

class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase, BaseSchema):
    pass

# Invoice Item
class InvoiceItemBase(BaseModel):
    product_id: int
    product_name_snapshot: str
    quantity: int = 1
    unit_price: float = 0.0
    line_total: float = 0.0
    note: Optional[str] = None

class InvoiceItemCreate(InvoiceItemBase):
    pass

class InvoiceItemResponse(InvoiceItemBase):
    id: int
    invoice_id: int

# Payment
class PaymentBase(BaseModel):
    method: str
    amount: float
    reference_code: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentResponse(PaymentBase):
    id: int
    invoice_id: int
    paid_at: datetime

# Invoice
class InvoiceBase(BaseModel):
    customer_id: Optional[int] = None
    subtotal: float = 0.0
    discount_amount: float = 0.0
    surcharge_amount: float = 0.0
    total_amount: float = 0.0
    payment_status: Optional[str] = "unpaid"
    invoice_status: Optional[str] = "valid"
    created_by: int

class InvoiceCreate(InvoiceBase):
    items: List[InvoiceItemCreate]
    payments: Optional[List[PaymentCreate]] = []

class InvoiceResponse(InvoiceBase, BaseSchema):
    invoice_code: str
    issued_at: Optional[datetime] = None
    items: List[InvoiceItemResponse] = []
    payments: List[PaymentResponse] = []
