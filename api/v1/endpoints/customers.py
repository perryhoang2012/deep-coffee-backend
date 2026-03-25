from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from models.customer import Customer
from schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from api.dependencies import get_current_active_user
from models.admin import User

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
