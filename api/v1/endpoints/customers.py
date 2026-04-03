import json
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from core.database import get_db
from models.customer import Customer, CustomerFace
from schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerFaceCreateRequest,
    CustomerFaceResponse,
)
from api.dependencies import get_current_active_user
from models.admin import User
from services.storage_service import StorageService
from services.vision_service import VisionService

router = APIRouter()

@router.post("/", response_model=CustomerResponse)
def create_customer(
    customer_in: CustomerCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    if customer_in.phone:
        existing = db.query(Customer).filter(Customer.phone == customer_in.phone).first()
        if existing:
            raise HTTPException(status_code=400, detail="Phone number already registered")
            
    db_customer = Customer(
        full_name=customer_in.full_name,
        phone=customer_in.phone,
        gender=customer_in.gender,
        birthday=customer_in.birthday,
        note=customer_in.note
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

@router.get("/", response_model=List[CustomerResponse])
def read_customers(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    customers = db.query(Customer).offset(skip).limit(limit).all()
    return customers

@router.get("/{customer_id}", response_model=CustomerResponse)
def read_customer(
    customer_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    customer_in: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    update_data = customer_in.model_dump(exclude_unset=True)
    if "phone" in update_data and update_data["phone"] != customer.phone:
        existing = db.query(Customer).filter(Customer.phone == update_data["phone"]).first()
        if existing:
            raise HTTPException(status_code=400, detail="Phone number already registered")
            
    for field, value in update_data.items():
        setattr(customer, field, value)
        
    db.commit()
    db.refresh(customer)
    return customer

@router.delete("/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    db.delete(customer)
    db.commit()
    return {"detail": "Customer deleted successfully"}

@router.get("/{customer_id}/faces", response_model=List[CustomerFaceResponse])
def read_customer_faces(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return db.query(CustomerFace).filter(CustomerFace.customer_id == customer_id).all()

@router.post("/{customer_id}/faces", response_model=CustomerFaceResponse)
def create_customer_face(
    customer_id: int,
    face_in: CustomerFaceCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    if face_in.is_primary:
        db.query(CustomerFace).filter(CustomerFace.customer_id == customer_id).update({"is_primary": False})

    db_face = CustomerFace(customer_id=customer_id, **face_in.model_dump())
    db.add(db_face)
    db.commit()
    db.refresh(db_face)
    return db_face

@router.post("/{customer_id}/faces/upload", response_model=CustomerFaceResponse)
async def upload_customer_face(
    customer_id: int,
    image: UploadFile = File(...),
    is_primary: bool = Form(default=False),
    quality_score: Optional[float] = Form(default=None),
    note: Optional[str] = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    image_bytes = await image.read()
    storage_service = StorageService()
    vision_result = VisionService().extract_face_embedding(image_bytes)
    if not vision_result["success"]:
        raise HTTPException(status_code=400, detail=vision_result.get("message") or vision_result["reason"])

    if is_primary:
        db.query(CustomerFace).filter(CustomerFace.customer_id == customer_id).update({"is_primary": False})

    saved_path = storage_service.save_customer_face(customer_id, image.filename or "face.jpg", image_bytes)
    db_face = CustomerFace(
        customer_id=customer_id,
        image_path=saved_path,
        embedding=json.dumps(vision_result["embedding"]),
        quality_score=quality_score,
        is_primary=is_primary,
        image_url=None,
    )
    if note:
        customer.note = f"{customer.note}\n{note}".strip() if customer.note else note

    db.add(db_face)
    db.commit()
    db.refresh(db_face)
    return db_face

@router.delete("/{customer_id}/faces/{face_id}")
def delete_customer_face(
    customer_id: int,
    face_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    face = (
        db.query(CustomerFace)
        .filter(CustomerFace.id == face_id, CustomerFace.customer_id == customer_id)
        .first()
    )
    if not face:
        raise HTTPException(status_code=404, detail="Customer face not found")

    db.delete(face)
    db.commit()
    return {"detail": "Customer face deleted successfully"}
