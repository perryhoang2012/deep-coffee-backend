from pydantic import BaseModel
from typing import Optional
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
