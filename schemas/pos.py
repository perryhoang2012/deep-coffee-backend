import re
import unicodedata

from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
from schemas.base import BaseSchema
from schemas.customer import CustomerResponse


STATUS_ALIASES = {
    "cho_xu_ly": "pending",
    "co_khach": "occupied",
    "con_hang": "in_stock",
    "da_hoan_tien": "refunded",
    "da_huy": "cancelled",
    "da_thanh_toan": "paid",
    "dang_ban": "active",
    "dang_hoat_dong": "active",
    "dang_xu_ly": "processing",
    "dat_truoc": "reserved",
    "het_hang": "out_of_stock",
    "hoan_thanh": "completed",
    "hoan_tien": "refunded",
    "hop_le": "valid",
    "huy": "cancelled",
    "huy_toan": "void",
    "khong_hoat_dong": "inactive",
    "sap_het": "low_stock",
    "tam_an": "inactive",
    "thanh_toan": "paid",
    "trong": "available",
}


def normalize_status_code(value: Optional[str]) -> Optional[str]:
    if value is None:
        return value

    normalized = unicodedata.normalize("NFD", str(value).strip().lower())
    normalized = "".join(char for char in normalized if unicodedata.category(char) != "Mn")
    normalized = normalized.replace("đ", "d")
    normalized = re.sub(r"[^a-z0-9]+", "_", normalized).strip("_")

    return STATUS_ALIASES.get(normalized, normalized)

# Category
class CategoryBase(BaseModel):
    name: str
    status: Optional[str] = "active"
    sort_order: Optional[int] = 0

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, value):
        return normalize_status_code(value)

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    sort_order: Optional[int] = None

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, value):
        return normalize_status_code(value)

class CategoryResponse(CategoryBase, BaseSchema):
    pass

# Product
class ProductBase(BaseModel):
    category_id: int
    sku: Optional[str] = None
    name: str
    price: float
    stock_quantity: int = 0
    low_stock_threshold: int = 5
    status: Optional[str] = "active"
    image_url: Optional[str] = None

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, value):
        return normalize_status_code(value)

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    category_id: Optional[int] = None
    sku: Optional[str] = None
    name: Optional[str] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None
    low_stock_threshold: Optional[int] = None
    status: Optional[str] = None
    image_url: Optional[str] = None

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, value):
        return normalize_status_code(value)

class ProductResponse(ProductBase, BaseSchema):
    pass

# Table
class TableBase(BaseModel):
    name: str
    area: Optional[str] = None
    status: Optional[str] = "available"
    capacity: Optional[int] = None

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, value):
        return normalize_status_code(value)

class TableCreate(TableBase):
    pass

class TableUpdate(BaseModel):
    name: Optional[str] = None
    area: Optional[str] = None
    status: Optional[str] = None
    capacity: Optional[int] = None

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, value):
        return normalize_status_code(value)

class TableResponse(TableBase, BaseSchema):
    pass

# Order
class OrderBase(BaseModel):
    table_id: Optional[int] = None
    customer_id: Optional[int] = None
    order_status: Optional[str] = "pending"
    created_by: int

    @field_validator("order_status", mode="before")
    @classmethod
    def normalize_order_status(cls, value):
        return normalize_status_code(value)

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
    table_id: Optional[int] = None
    subtotal: float = 0.0
    discount_amount: float = 0.0
    surcharge_amount: float = 0.0
    total_amount: float = 0.0
    payment_status: Optional[str] = "unpaid"
    invoice_status: Optional[str] = "valid"
    created_by: Optional[int] = None

    @field_validator("payment_status", "invoice_status", mode="before")
    @classmethod
    def normalize_invoice_status(cls, value):
        return normalize_status_code(value)

class InvoiceCreate(InvoiceBase):
    items: List[InvoiceItemCreate]
    payments: Optional[List[PaymentCreate]] = []

class InvoiceResponse(InvoiceBase, BaseSchema):
    invoice_code: str
    issued_at: Optional[datetime] = None
    items: List[InvoiceItemResponse] = []
    payments: List[PaymentResponse] = []
    table: Optional[TableResponse] = None
    customer: Optional[CustomerResponse] = None
