from sqlalchemy import Column, String
from models.base import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, default="staff")
    status = Column(String, default="active")

class SystemSetting(BaseModel):
    __tablename__ = "system_settings"
    
    key = Column(String, unique=True, index=True, nullable=False)
    value = Column(String, nullable=False)
    description = Column(String, nullable=True)
