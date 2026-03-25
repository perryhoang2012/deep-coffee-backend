from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
from models.base import BaseModel

class Customer(BaseModel):
    __tablename__ = "customers"
    
    full_name = Column(String, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=True)
    gender = Column(String, nullable=True) # male, female, other
    birthday = Column(Date, nullable=True)
    note = Column(String, nullable=True)
    
    # relationships can be added here if needed, like invoices

class CustomerFace(BaseModel):
    __tablename__ = "customer_faces"
    
    customer_id = Column(Integer, ForeignKey("customers.id"))
    image_path = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    embedding = Column(String, nullable=True) # Should ideally be array or vector type if postgis/pgvector is used
    quality_score = Column(Float, nullable=True)
    is_primary = Column(Boolean, default=False)
