from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from schemas.base import BaseSchema

# Customer Face
class CustomerFaceBase(BaseModel):
    image_path: Optional[str] = None
    image_url: Optional[str] = None
    embedding: Optional[str] = None
    quality_score: Optional[float] = None
    is_primary: Optional[bool] = False

class CustomerFaceCreate(CustomerFaceBase):
    customer_id: int

class CustomerFaceCreateRequest(CustomerFaceBase):
    pass

class CustomerFaceResponse(CustomerFaceBase, BaseSchema):
    customer_id: int

# Customer
class CustomerBase(BaseModel):
    full_name: str
    phone: Optional[str] = None
    gender: Optional[str] = None
    birthday: Optional[date] = None
    note: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    birthday: Optional[date] = None
    note: Optional[str] = None

class CustomerResponse(CustomerBase, BaseSchema):
    faces: Optional[List[CustomerFaceResponse]] = []
