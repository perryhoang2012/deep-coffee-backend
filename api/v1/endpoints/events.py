import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from core.database import get_db
from api.dependencies import get_current_active_user
from models.admin import User
from models.customer import Customer, CustomerFace
from models.event import Camera, GreetingEvent, RecognitionEvent
from models.pos import Invoice
from schemas.event import (
    CameraCreate,
    CameraResponse,
    CameraUpdate,
    GreetingEventResponse,
    LoyalCustomerRecognitionResponse,
    LoyaltyCheckResponse,
    RecognitionEventResponse,
    RecognitionProcessResponse,
    RecognitionRequest,
)
from services.greeting_service import GreetingService
from services.loyalty_service import LoyaltyService
from services.recognition_service import RecognitionService
from services.storage_service import StorageService
from services.vision_service import VisionService
from services.customer_face_retention import prune_customer_faces

router = APIRouter()


def _get_or_create_camera(
    db: Session,
    camera_id: str,
    branch_id: Optional[str] = None,
) -> Camera:
    normalized_camera_id = (camera_id or "browser_loyal_customer_camera").strip()
    if not normalized_camera_id:
        normalized_camera_id = "browser_loyal_customer_camera"

    if normalized_camera_id.isdigit():
        camera = db.query(Camera).filter(Camera.id == int(normalized_camera_id)).first()
        if camera:
            return camera

    camera = db.query(Camera).filter(Camera.name == normalized_camera_id).first()
    if camera:
        if branch_id and not camera.location:
            camera.location = branch_id
            db.commit()
            db.refresh(camera)
        return camera

    camera = Camera(
        name=normalized_camera_id,
        location=branch_id,
        status="active",
        stream_source="browser",
    )
    db.add(camera)
    db.commit()
    db.refresh(camera)
    return camera


def _build_recognition_failure_message(reason: Optional[str], detail: Optional[str] = None) -> str:
    if detail:
        return detail

    return {
        "no_face_detected": "Không phát hiện khuôn mặt trong khung hình",
        "invalid_image": "Ảnh gửi lên không hợp lệ",
        "missing_dependency": "Backend chưa sẵn sàng cho xử lý thị giác máy tính",
    }.get(reason or "", "Không thể xử lý ảnh nhận diện")

@router.post("/recognition", response_model=RecognitionProcessResponse)
def handle_recognition_event(
    payload: RecognitionRequest,
    db: Session = Depends(get_db)
):
    recognition_service = RecognitionService(db)
    return recognition_service.process_recognition_event(payload)

@router.get("/recognition/image")
def recognition_image_usage():
    return {
        "status": "method_not_allowed_for_inference",
        "message": "Use POST /api/v1/events/recognition/image with multipart/form-data and an image file.",
        "required_fields": ["camera_id", "image"],
        "optional_fields": ["customer_id", "recognized_at"],
    }

@router.post("/recognition/image")
async def handle_recognition_image(
    camera_id: str = Form(...),
    image: UploadFile = File(...),
    customer_id: Optional[int] = Form(default=None),
    recognized_at: Optional[str] = Form(default=None),
    db: Session = Depends(get_db),
):
    vision_service = VisionService()
    image_bytes = await image.read()
    snapshot_path = StorageService().save_recognition_snapshot(camera_id, image.filename or "capture.jpg", image_bytes)
    vision_result = vision_service.extract_face_embedding(image_bytes)

    if not vision_result["success"]:
        return {
            "status": "failed",
            "reason": vision_result["reason"],
            "message": vision_result.get("message"),
            "detector_used": vision_result["detector_used"],
            "faces_detected": vision_result["faces_detected"],
            "snapshot_path": snapshot_path,
        }

    payload = RecognitionRequest(
        camera_id=int(camera_id) if camera_id.isdigit() else camera_id,
        customer_id=customer_id,
        embedding=vision_result["embedding"],
        snapshot_path=snapshot_path,
        recognized_at=recognized_at,
    )

    recognition_result = RecognitionService(db).process_recognition_event(payload)
    recognition_result["detector_used"] = vision_result["detector_used"]
    recognition_result["faces_detected"] = vision_result["faces_detected"]
    recognition_result["bounding_box"] = vision_result["bounding_box"]
    recognition_result["snapshot_path"] = snapshot_path
    return recognition_result


@router.post(
    "/loyal-customers/recognize-face",
    response_model=LoyalCustomerRecognitionResponse,
)
async def recognize_loyal_customer_face(
    camera_id: str = Form(default="browser_loyal_customer_camera"),
    image: UploadFile = File(...),
    branch_id: Optional[str] = Form(default=None),
    recognized_at: Optional[str] = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    del current_user

    camera = _get_or_create_camera(db, camera_id, branch_id)
    image_bytes = await image.read()
    snapshot_path = StorageService().save_recognition_snapshot(
        camera.name,
        image.filename or "capture.jpg",
        image_bytes,
    )

    vision_result = VisionService().extract_face_embedding(image_bytes)
    if not vision_result["success"]:
        return {
            "matched": False,
            "is_loyal": False,
            "customer": None,
            "greeting_text": None,
            "audio_url": None,
            "confidence": None,
            "message": _build_recognition_failure_message(
                vision_result.get("reason"),
                vision_result.get("message"),
            ),
            "recognition_status": vision_result.get("reason"),
            "was_greeted": False,
            "detector_used": vision_result.get("detector_used"),
            "faces_detected": vision_result.get("faces_detected", 0),
            "snapshot_path": snapshot_path,
            "recognized_at": datetime.utcnow(),
            "camera_id": camera.name,
            "branch_id": branch_id,
        }

    payload = RecognitionRequest(
        camera_id=camera.id,
        embedding=vision_result["embedding"],
        snapshot_path=snapshot_path,
        recognized_at=recognized_at,
    )

    recognition_result = RecognitionService(db).process_recognition_event(payload)
    matched_customer_id = recognition_result.get("matched_customer_id")
    matched_customer = None
    if matched_customer_id is not None:
        matched_customer = db.query(Customer).filter(Customer.id == matched_customer_id).first()

    if not matched_customer:
        return {
            "matched": False,
            "is_loyal": False,
            "customer": None,
            "greeting_text": None,
            "audio_url": None,
            "confidence": recognition_result.get("confidence"),
            "message": "Không tìm thấy khách hàng phù hợp",
            "recognition_status": recognition_result.get("recognition_status"),
            "was_greeted": recognition_result.get("was_greeted", False),
            "detector_used": vision_result.get("detector_used"),
            "faces_detected": vision_result.get("faces_detected", 0),
            "snapshot_path": snapshot_path,
            "recognized_at": recognition_result.get("recognized_at"),
            "camera_id": camera.name,
            "branch_id": branch_id,
        }

    loyalty_result = LoyaltyService(db).check_customer_loyalty(matched_customer.id)
    is_loyal = loyalty_result.get("qualified", False)
    was_greeted = recognition_result.get("was_greeted", False)
    greeting_text = (
        GreetingService(db).build_greeting_message(matched_customer)
        if is_loyal and was_greeted
        else None
    )

    if is_loyal:
        if was_greeted:
            message = "Đã nhận diện khách hàng thân thiết"
        else:
            message = (
                "Đã nhận diện khách hàng thân thiết, nhưng đang trong thời gian chờ "
                "5 phút trước khi phát lời chào tiếp theo"
            )
    else:
        message = "Đã nhận diện khách hàng nhưng chưa đạt ngưỡng thân thiết"

    return {
        "matched": True,
        "is_loyal": is_loyal,
        "customer": {
            "id": matched_customer.id,
            "name": matched_customer.full_name,
            "phone": matched_customer.phone,
            "total_orders": loyalty_result.get("total_orders", 0),
            "recent_orders": loyalty_result.get("invoice_count_period", 0),
            "loyal_status": "loyal" if is_loyal else "regular",
        },
        "greeting_text": greeting_text,
        "audio_url": None,
        "confidence": recognition_result.get("confidence"),
        "message": message,
        "recognition_status": recognition_result.get("recognition_status"),
        "was_greeted": was_greeted,
        "detector_used": vision_result.get("detector_used"),
        "faces_detected": vision_result.get("faces_detected", 0),
        "snapshot_path": snapshot_path,
        "recognized_at": recognition_result.get("recognized_at"),
        "camera_id": camera.name,
        "branch_id": branch_id,
    }

@router.post("/test-scenario/register-face")
async def register_face_for_test(
    customer_id: int = Form(...),
    image: UploadFile = File(...),
    is_primary: bool = Form(default=True),
    db: Session = Depends(get_db),
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    image_bytes = await image.read()
    vision_result = VisionService().extract_face_embedding(image_bytes)
    if not vision_result["success"]:
        raise HTTPException(status_code=400, detail=vision_result.get("message") or vision_result["reason"])

    if is_primary:
        db.query(CustomerFace).filter(CustomerFace.customer_id == customer_id).update({"is_primary": False})

    saved_path = StorageService().save_customer_face(customer_id, image.filename or "face.jpg", image_bytes)
    db_face = CustomerFace(
        customer_id=customer_id,
        image_path=saved_path,
        image_url=None,
        embedding=json.dumps(vision_result["embedding"]),
        quality_score=None,
        is_primary=is_primary,
    )
    db.add(db_face)
    prune_customer_faces(db, customer_id)
    db.commit()
    db.refresh(db_face)

    return {
        "status": "ok",
        "customer_id": customer_id,
        "customer_name": customer.full_name,
        "face_id": db_face.id,
        "image_path": db_face.image_path,
        "detector_used": vision_result["detector_used"],
        "faces_detected": vision_result["faces_detected"],
    }

@router.post("/test-scenario/seed-loyal-customer")
def seed_loyal_customer_scenario(
    customer_id: int = Form(...),
    camera_id: str = Form("cam_01"),
    duplicate_faces: int = Form(10),
    invoice_days: int = Form(10),
    db: Session = Depends(get_db),
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    if duplicate_faces < 1:
        duplicate_faces = 1
    if invoice_days < 1:
        invoice_days = 1

    camera = db.query(Camera).filter(Camera.name == camera_id).first()
    if not camera:
        camera = Camera(name=camera_id, location="Test Area", status="active")
        db.add(camera)
        db.commit()
        db.refresh(camera)

    source_face = (
        db.query(CustomerFace)
        .filter(CustomerFace.customer_id == customer_id)
        .order_by(CustomerFace.is_primary.desc(), CustomerFace.id.asc())
        .first()
    )
    if not source_face or not source_face.image_path:
        raise HTTPException(status_code=400, detail="Customer does not have a saved face image to duplicate")

    duplicated_face_ids = []
    source_path = Path(source_face.image_path)
    if source_path.exists():
        for index in range(duplicate_faces):
            target_name = f"copy_{index + 1:02d}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:6]}{source_path.suffix or '.jpg'}"
            target_path = source_path.parent / target_name
            shutil.copy2(source_path, target_path)
            new_face = CustomerFace(
                customer_id=customer_id,
                image_path=str(target_path),
                image_url=None,
                embedding=source_face.embedding,
                quality_score=source_face.quality_score,
                is_primary=False,
            )
            db.add(new_face)
            db.flush()
            duplicated_face_ids.append(new_face.id)

    prune_customer_faces(db, customer_id)

    created_invoice_codes = []
    creator = db.query(User).order_by(User.id.asc()).first()
    existing_recent_invoices = (
        db.query(Invoice)
        .filter(
            Invoice.customer_id == customer_id,
            Invoice.invoice_status == "valid",
            Invoice.issued_at >= datetime.utcnow() - timedelta(days=30),
        )
        .count()
    )
    invoices_to_create = max(0, 10 - existing_recent_invoices)
    invoices_to_create = max(invoices_to_create, invoice_days)

    for index in range(invoices_to_create):
        issued_at = datetime.utcnow() - timedelta(days=min(index, 29))
        invoice_code = f"LOYAL-{customer_id}-{uuid4().hex[:8].upper()}"
        invoice = Invoice(
            customer_id=customer_id,
            invoice_code=invoice_code,
            subtotal=50000.0,
            discount_amount=0.0,
            surcharge_amount=0.0,
            total_amount=50000.0,
            payment_status="paid",
            invoice_status="valid",
            created_by=creator.id if creator else None,
            issued_at=issued_at,
        )
        db.add(invoice)
        created_invoice_codes.append(invoice_code)

    db.commit()

    loyalty_result = LoyaltyService(db).check_customer_loyalty(customer_id)
    return {
        "status": "ok",
        "customer_id": customer_id,
        "customer_name": customer.full_name,
        "camera_id": camera.name,
        "duplicated_faces": len(duplicated_face_ids),
        "duplicated_face_ids": duplicated_face_ids,
        "created_invoices": len(created_invoice_codes),
        "created_invoice_codes": created_invoice_codes,
        "invoice_count_30d": loyalty_result["invoice_count_30d"],
        "qualified": loyalty_result["qualified"],
        "next_step": "Open /face-test, choose the same camera_id, leave customer_id blank or set it to this customer, then click 'Chup va nhan dien'.",
    }

@router.post("/test-scenario/reset-greeting-cooldown")
def reset_greeting_cooldown(
    customer_id: int = Form(...),
    db: Session = Depends(get_db),
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    deleted_greetings = (
        db.query(GreetingEvent)
        .filter(GreetingEvent.customer_id == customer_id)
        .delete(synchronize_session=False)
    )
    db.commit()

    return {
        "status": "ok",
        "customer_id": customer_id,
        "customer_name": customer.full_name,
        "deleted_greeting_events": deleted_greetings,
        "message": "Greeting cooldown has been reset for this customer.",
    }

@router.get("/cameras", response_model=List[CameraResponse])
def read_cameras(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return db.query(Camera).order_by(Camera.id.desc()).all()

@router.post("/cameras", response_model=CameraResponse)
def create_camera(
    camera_in: CameraCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_camera = Camera(**camera_in.model_dump())
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    return db_camera

@router.put("/cameras/{camera_id}", response_model=CameraResponse)
def update_camera(
    camera_id: int,
    camera_in: CameraUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    for field, value in camera_in.model_dump(exclude_unset=True).items():
        setattr(camera, field, value)

    db.commit()
    db.refresh(camera)
    return camera

@router.get("/recognition-events", response_model=List[RecognitionEventResponse])
def read_recognition_events(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return (
        db.query(RecognitionEvent)
        .order_by(RecognitionEvent.recognized_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

@router.get("/greeting-events", response_model=List[GreetingEventResponse])
def read_greeting_events(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return (
        db.query(GreetingEvent)
        .order_by(GreetingEvent.greeted_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

@router.get("/loyalty/{customer_id}", response_model=LoyaltyCheckResponse)
def check_customer_loyalty(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    loyalty_result = LoyaltyService(db).check_customer_loyalty(customer_id)
    return {
        "customer_id": customer_id,
        "qualified": loyalty_result["qualified"],
        "invoice_count_30d": loyalty_result["invoice_count_30d"],
        "invoice_required": loyalty_result["invoice_required"],
        "days_window": loyalty_result["days_window"],
    }
