from pydantic import BaseModel, ConfigDict
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from schemas.base import BaseSchema

# Camera
class CameraBase(BaseModel):
    name: str
    location: Optional[str] = None
    status: Optional[str] = "active"
    stream_source: Optional[str] = None

class CameraCreate(CameraBase):
    pass

class CameraUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    stream_source: Optional[str] = None

class CameraResponse(CameraBase, BaseSchema):
    pass

# Recognition Event
class RecognitionEventBase(BaseModel):
    camera_id: int
    customer_id: Optional[int] = None
    confidence: Optional[float] = None
    snapshot_path: Optional[str] = None
    result_status: Optional[str] = "matched"
    recognized_at: datetime

class RecognitionEventCreate(RecognitionEventBase):
    pass

class RecognitionEventResponse(RecognitionEventBase, BaseSchema):
    pass

# Greeting Event
class GreetingEventBase(BaseModel):
    recognition_event_id: int
    customer_id: int
    greeting_message: str
    status: Optional[str] = "triggered"
    greeted_at: datetime

class GreetingEventCreate(GreetingEventBase):
    pass

class GreetingEventResponse(GreetingEventBase, BaseSchema):
    pass

class RecognitionRequest(BaseModel):
    camera_id: Union[int, str]
    embedding: Optional[List[float]] = None
    customer_id: Optional[int] = None
    confidence: Optional[float] = None
    snapshot_path: Optional[str] = None
    recognized_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class LoyaltyCheckResponse(BaseModel):
    customer_id: int
    qualified: bool
    invoice_count_30d: int
    invoice_required: int
    days_window: int

class RecognitionProcessResponse(BaseModel):
    status: str
    reason: str
    recognition_event_id: Optional[int] = None
    greeting_event_id: Optional[int] = None
    matched_customer_id: Optional[int] = None
    matched_customer_name: Optional[str] = None
    confidence: Optional[float] = None
    recognition_status: Optional[str] = None
    was_greeted: bool = False
    loyal_customer: bool = False
    invoice_count_30d: int = 0
    greeting_message: Optional[str] = None
    recognized_at: datetime

    model_config = ConfigDict(extra="ignore")


class SeedLoyalCustomerRequest(BaseModel):
    customer_id: int
    camera_id: str = "cam_01"
    duplicate_faces: int = 10
    invoice_days: int = 10


class ResetGreetingCooldownRequest(BaseModel):
    customer_id: int
