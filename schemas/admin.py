from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, time
from schemas.base import BaseSchema

# User Schemas
class UserBase(BaseModel):
    username: str
    full_name: str
    role: Optional[str] = "staff"
    status: Optional[str] = "active"

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    password: Optional[str] = None

class UserResponse(UserBase, BaseSchema):
    pass

# Employee Shift Schemas
class EmployeeShiftBase(BaseModel):
    user_id: int
    shift_date: date
    start_time: time
    end_time: time
    status: Optional[str] = "scheduled"

class EmployeeShiftCreate(EmployeeShiftBase):
    pass

class EmployeeShiftResponse(EmployeeShiftBase, BaseSchema):
    pass

# System Setting Schemas
class SystemSettingBase(BaseModel):
    key: str
    value: str
    description: Optional[str] = None

class SystemSettingCreate(SystemSettingBase):
    pass

class SystemSettingResponse(SystemSettingBase, BaseSchema):
    pass
