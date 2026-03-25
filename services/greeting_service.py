from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, Any

from models.event import RecognitionEvent, GreetingEvent
from services.loyalty_service import LoyaltyService

class GreetingService:
    def __init__(self, db: Session):
        self.db = db
        self.loyalty_service = LoyaltyService(db)

    def process_recognition_event(self, recognition_payload: Dict[str, Any]) -> dict:
        """
        Process a new recognition event from AI/CV model.
        Payload format matches Document:
        {
          "camera_id": "cam_01",  # Assuming int ID is used or string mapping
          "customer_id": 123,
          "confidence": 0.92,
          "snapshot_path": "/path/to/img",
          "recognized_at": "..."
        }
        """
        # Save Recognition Event
        camera_db_id = 1 # Simplified for now
        customer_id = recognition_payload.get("customer_id")
        confidence = recognition_payload.get("confidence", 0.0)
        
        event = RecognitionEvent(
            camera_id=camera_db_id,
            customer_id=customer_id,
            confidence=confidence,
            snapshot_path=recognition_payload.get("snapshot_path"),
            result_status="matched" if customer_id and confidence > 0.8 else "unknown",
            recognized_at=datetime.utcnow()
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)

        # Check rules for Greeting
        greeted = False
        greeting_event = None
        
        if event.result_status == "matched":
            # 1. Loyalty Check
            loyalty_result = self.loyalty_service.check_customer_loyalty(customer_id)
            
            if loyalty_result["qualified"]:
                # 2. Cooldown check (e.g., has been greeted in the last 12 hours)
                cooldown_threshold = datetime.utcnow() - timedelta(hours=12)
                recent_greeting = self.db.query(GreetingEvent).filter(
                    GreetingEvent.customer_id == customer_id,
                    GreetingEvent.greeted_at >= cooldown_threshold
                ).first()

                if not recent_greeting:
                    # 3. Trigger Greeting
                    customer_name = loyalty_result["customer"].full_name if loyalty_result["customer"] else "Quý khách"
                    message = f"Xin chào anh/chị {customer_name}, rất vui được gặp lại nhà đầu tư tại quán."
                    
                    greeting_event = GreetingEvent(
                        recognition_event_id=event.id,
                        customer_id=customer_id,
                        greeting_message=message,
                        status="triggered",
                        greeted_at=datetime.utcnow()
                    )
                    self.db.add(greeting_event)
                    self.db.commit()
                    self.db.refresh(greeting_event)
                    greeted = True
                    
                    # NOTE: Here we would trigger WebSocket payload for UI
                    # This will be handled in the routers or WebSocket manager.

        return {
            "recognition_event": event,
            "greeting_event": greeting_event,
            "was_greeted": greeted
        }
