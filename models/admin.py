from sqlalchemy import Column, String, Boolean, Date, Time, ForeignKey, Integer
from models.base import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, default="staff") # admin, manager, staff
    status = Column(String, default="active") # active, inactive

class EmployeeShift(BaseModel):
    __tablename__ = "employee_shifts"
    
    user_id = Column(Integer, ForeignKey("users.id"))
    shift_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    status = Column(String, default="scheduled") # scheduled, in_progress, completed

class SystemSetting(BaseModel):
    __tablename__ = "system_settings"
    
    key = Column(String, unique=True, index=True, nullable=False)
    value = Column(String, nullable=False)
    description = Column(String, nullable=True)
