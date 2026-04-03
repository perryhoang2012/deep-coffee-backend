from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from models.base import BaseModel

class Camera(BaseModel):
    __tablename__ = "cameras"
    
    name = Column(String, nullable=False)
    location = Column(String, nullable=True)
    status = Column(String, default="active") # active, inactive, offline
    stream_source = Column(String, nullable=True)

    recognition_events = relationship("RecognitionEvent", back_populates="camera")

class RecognitionEvent(BaseModel):
    __tablename__ = "recognition_events"
    
    camera_id = Column(Integer, ForeignKey("cameras.id"))
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    confidence = Column(Float, nullable=True)
    snapshot_path = Column(String, nullable=True)
    result_status = Column(String, default="matched") # matched, unknown, skipped
    recognized_at = Column(DateTime, nullable=False)

    camera = relationship("Camera", back_populates="recognition_events")
    greeting_events = relationship("GreetingEvent", back_populates="recognition_event")

class GreetingEvent(BaseModel):
    __tablename__ = "greeting_events"
    
    recognition_event_id = Column(Integer, ForeignKey("recognition_events.id"))
    customer_id = Column(Integer, ForeignKey("customers.id"))
    greeting_message = Column(String, nullable=False)
    status = Column(String, default="triggered") # triggered, failed
    greeted_at = Column(DateTime, nullable=False)

    recognition_event = relationship("RecognitionEvent", back_populates="greeting_events")
