from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from api.v1.websockets.dashboard import manager
from core.config import settings
from models.customer import Customer
from models.event import Camera, RecognitionEvent
from services.face_recognition_service import FaceRecognitionService
from services.greeting_service import GreetingService
from services.loyalty_service import LoyaltyService


class RecognitionService:
    def __init__(self, db: Session):
        self.db = db
        self.face_service = FaceRecognitionService(db)
        self.loyalty_service = LoyaltyService(db)
        self.greeting_service = GreetingService(db)

    def process_recognition_event(self, payload) -> dict:
        recognized_at = payload.recognized_at or datetime.utcnow()
        camera = self._resolve_camera(payload.camera_id)

        if not camera:
            manager.publish(
                {
                    "event": "system.alert",
                    "level": "warning",
                    "message": f"Camera {payload.camera_id} was not found",
                    "created_at": recognized_at.isoformat(),
                }
            )
            return self._build_result(
                status="failed",
                reason="camera_not_found",
                recognized_at=recognized_at,
            )

        if camera.status != "active":
            recognition_event = self._create_recognition_event(
                camera=camera,
                recognized_at=recognized_at,
                snapshot_path=payload.snapshot_path,
                result_status="camera_inactive",
            )
            manager.publish(
                {
                    "event": "camera.status_changed",
                    "camera_id": camera.id,
                    "camera_name": camera.name,
                    "status": camera.status,
                    "recognized_at": recognized_at.isoformat(),
                }
            )
            return self._build_result(
                status="success",
                reason="camera_inactive",
                recognition_event=recognition_event,
                recognition_status=recognition_event.result_status,
                recognized_at=recognized_at,
            )

        matched_customer, confidence = self._resolve_customer_match(payload)
        if not matched_customer:
            recognition_event = self._create_recognition_event(
                camera=camera,
                recognized_at=recognized_at,
                snapshot_path=payload.snapshot_path,
                confidence=confidence,
                result_status="unknown" if confidence is None else "low_confidence",
            )
            manager.publish(
                {
                    "event": "recognition.detected",
                    "camera_id": camera.id,
                    "camera_name": camera.name,
                    "recognized_at": recognized_at.isoformat(),
                    "confidence": confidence,
                    "status": recognition_event.result_status,
                }
            )
            return self._build_result(
                status="success",
                reason=recognition_event.result_status,
                recognition_event=recognition_event,
                confidence=confidence,
                recognition_status=recognition_event.result_status,
                recognized_at=recognized_at,
            )

        duplicate_recent = self._find_recent_duplicate(camera.id, matched_customer.id, recognized_at)
        recognition_status = "duplicate" if duplicate_recent else "matched"
        recognition_event = self._create_recognition_event(
            camera=camera,
            recognized_at=recognized_at,
            snapshot_path=payload.snapshot_path,
            customer_id=matched_customer.id,
            confidence=confidence,
            result_status=recognition_status,
        )

        manager.publish(
            {
                "event": "recognition.matched",
                "camera_id": camera.id,
                "camera_name": camera.name,
                "customer_id": matched_customer.id,
                "customer_name": matched_customer.full_name,
                "confidence": confidence,
                "recognized_at": recognized_at.isoformat(),
            }
        )

        loyalty_result = self.loyalty_service.check_customer_loyalty(matched_customer.id)
        manager.publish(
            {
                "event": "loyal_customer.verified",
                "customer_id": matched_customer.id,
                "customer_name": matched_customer.full_name,
                "invoice_count_30d": loyalty_result["invoice_count_30d"],
                "qualified": loyalty_result["qualified"],
                "checked_at": datetime.utcnow().isoformat(),
            }
        )

        if duplicate_recent:
            return self._build_result(
                status="success",
                reason="duplicate_recognition",
                recognition_event=recognition_event,
                matched_customer=matched_customer,
                confidence=confidence,
                recognition_status=recognition_status,
                recognized_at=recognized_at,
                loyalty_result=loyalty_result,
            )

        greeting_result = self.greeting_service.trigger_greeting(
            recognition_event=recognition_event,
            customer=matched_customer,
            loyalty_result=loyalty_result,
            greeted_at=recognized_at,
        )

        if greeting_result["greeting_event"]:
            manager.publish(
                {
                    "event": "greeting.triggered",
                    "customer_id": matched_customer.id,
                    "customer_name": matched_customer.full_name,
                    "message": greeting_result["greeting_event"].greeting_message,
                    "greeted_at": greeting_result["greeting_event"].greeted_at.isoformat(),
                }
            )

        return self._build_result(
            status="success",
            reason=greeting_result["reason"],
            recognition_event=recognition_event,
            greeting_event=greeting_result["greeting_event"],
            matched_customer=matched_customer,
            confidence=confidence,
            recognition_status=recognition_status,
            recognized_at=recognized_at,
            loyalty_result=loyalty_result,
        )

    def _resolve_camera(self, camera_identifier) -> Optional[Camera]:
        if isinstance(camera_identifier, int):
            return self.db.query(Camera).filter(Camera.id == camera_identifier).first()

        return self.db.query(Camera).filter(Camera.name == str(camera_identifier)).first()

    def _resolve_customer_match(self, payload) -> tuple[Optional[Customer], Optional[float]]:
        if payload.customer_id is not None:
            customer = self.db.query(Customer).filter(Customer.id == payload.customer_id).first()
            return customer, payload.confidence or 1.0

        match_result = self.face_service.match_customer(payload.embedding)
        return match_result["customer"], match_result["confidence"]

    def _find_recent_duplicate(self, camera_id: int, customer_id: int, recognized_at: datetime) -> Optional[RecognitionEvent]:
        threshold = recognized_at - timedelta(seconds=settings.RECOGNITION_DUPLICATE_WINDOW_SECONDS)
        return (
            self.db.query(RecognitionEvent)
            .filter(
                RecognitionEvent.camera_id == camera_id,
                RecognitionEvent.customer_id == customer_id,
                RecognitionEvent.result_status == "matched",
                RecognitionEvent.recognized_at >= threshold,
            )
            .order_by(RecognitionEvent.recognized_at.desc())
            .first()
        )

    def _create_recognition_event(
        self,
        camera: Camera,
        recognized_at: datetime,
        snapshot_path: Optional[str],
        customer_id: Optional[int] = None,
        confidence: Optional[float] = None,
        result_status: str = "unknown",
    ) -> RecognitionEvent:
        event = RecognitionEvent(
            camera_id=camera.id,
            customer_id=customer_id,
            confidence=confidence,
            snapshot_path=snapshot_path,
            result_status=result_status,
            recognized_at=recognized_at,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def _build_result(
        self,
        status: str,
        reason: str,
        recognized_at: datetime,
        recognition_event: Optional[RecognitionEvent] = None,
        greeting_event=None,
        matched_customer: Optional[Customer] = None,
        confidence: Optional[float] = None,
        recognition_status: Optional[str] = None,
        loyalty_result: Optional[dict] = None,
    ) -> dict:
        loyalty_result = loyalty_result or {}
        return {
            "status": status,
            "reason": reason,
            "recognition_event_id": recognition_event.id if recognition_event else None,
            "greeting_event_id": greeting_event.id if greeting_event else None,
            "matched_customer_id": matched_customer.id if matched_customer else None,
            "matched_customer_name": matched_customer.full_name if matched_customer else None,
            "confidence": confidence,
            "recognition_status": recognition_status,
            "was_greeted": greeting_event is not None,
            "loyal_customer": loyalty_result.get("qualified", False),
            "invoice_count_30d": loyalty_result.get("invoice_count_30d", 0),
            "greeting_message": greeting_event.greeting_message if greeting_event else None,
            "recognized_at": recognized_at,
        }
