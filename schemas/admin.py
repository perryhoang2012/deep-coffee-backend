from pydantic import BaseModel
from typing import Optional
from schemas.base import BaseSchema


class UserBase(BaseModel):
    username: str
    full_name: str
    role: Optional[str] = "staff"
    status: Optional[str] = "active"

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    password: Optional[str] = None

class UserResponse(UserBase, BaseSchema):
    pass


class SystemSettingBase(BaseModel):
    key: str
    value: str
    description: Optional[str] = None

class SystemSettingCreate(SystemSettingBase):
    pass

class SystemSettingUpdate(BaseModel):
    value: Optional[str] = None
    description: Optional[str] = None

class SystemSettingUpsert(BaseModel):
    value: str
    description: Optional[str] = None

class SystemSettingResponse(SystemSettingBase, BaseSchema):
    pass
