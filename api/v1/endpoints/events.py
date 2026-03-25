from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.event import RecognitionEventCreate
from services.greeting_service import GreetingService

router = APIRouter()

@router.post("/recognition")
def handle_recognition_event(
    payload: Dict[str, Any], 
    db: Session = Depends(get_db)
):
    """
    Endpoint for the AI/CV module to send recognition events.
    Payload Example:
    {
      "camera_id": "cam_01",
      "customer_id": 123,
      "confidence": 0.92,
      "snapshot_path": "/path/images/123.jpg"
    }
    """
    greeting_service = GreetingService(db)
    result = greeting_service.process_recognition_event(payload)
    
    return {
        "status": "success",
        "was_greeted": result["was_greeted"],
        "recognition_event_id": result["recognition_event"].id if result["recognition_event"] else None,
        "greeting_event_id": result["greeting_event"].id if result["greeting_event"] else None
    }
