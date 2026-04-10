from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from core.config import settings
from models.customer import Customer
from models.event import GreetingEvent, RecognitionEvent

class GreetingService:
    def __init__(self, db: Session):
        self.db = db

    def trigger_greeting(
        self,
        recognition_event: RecognitionEvent,
        customer: Customer,
        loyalty_result: dict,
        greeted_at: Optional[datetime] = None,
    ) -> dict:
        if not loyalty_result.get("qualified"):
            return {"greeting_event": None, "reason": "not_loyal_customer"}

        greeted_at = greeted_at or datetime.utcnow()
        cooldown_threshold = greeted_at - timedelta(hours=settings.GREETING_COOLDOWN_HOURS)
        recent_greeting = (
            self.db.query(GreetingEvent)
            .filter(
                GreetingEvent.customer_id == customer.id,
                GreetingEvent.greeted_at >= cooldown_threshold,
            )
            .order_by(GreetingEvent.greeted_at.desc())
            .first()
        )
        if recent_greeting:
            return {"greeting_event": None, "reason": "greeting_cooldown_active"}

        message = self.build_greeting_message(customer)
        greeting_event = GreetingEvent(
            recognition_event_id=recognition_event.id,
            customer_id=customer.id,
            greeting_message=message,
            status="triggered",
            greeted_at=greeted_at,
        )
        self.db.add(greeting_event)
        self.db.commit()
        self.db.refresh(greeting_event)
        return {"greeting_event": greeting_event, "reason": "greeting_triggered"}

    def build_greeting_message(self, customer: Customer) -> str:
        return f"Xin Chào {customer.full_name}, rất vui được gặp lại bạn"
