from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session
from core.database import get_db
from core.pagination import paginate_query
from models.admin import User
from schemas.admin import UserCreate, UserUpdate, UserResponse
from schemas.base import PaginatedResponse
from core.security import get_password_hash
from api.dependencies import get_current_active_user

router = APIRouter()

USER_SORT_FIELDS = {
    "id": User.id,
    "username": User.username,
    "full_name": User.full_name,
    "role": User.role,
    "status": User.status,
    "created_at": User.created_at,
    "updated_at": User.updated_at,
}

@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.post("/", response_model=UserResponse)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_in.username).first()
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")
        
    db_user = User(
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        status=user_in.status
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/", response_model=PaginatedResponse[UserResponse])
def read_users(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    skip: int | None = Query(default=None, ge=0),
    search: str | None = Query(default=None),
    status: str | None = Query(default=None),
    sort_by: str = Query(default="id"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    users_query = db.query(User)

    if search:
        search_term = f"%{search.strip()}%"
        users_query = users_query.filter(
            or_(
                User.username.ilike(search_term),
                User.full_name.ilike(search_term),
            )
        )

    if status:
        users_query = users_query.filter(User.status == status)

    sort_column = USER_SORT_FIELDS.get(sort_by, User.id)
    sort_expression = asc(sort_column) if sort_order == "asc" else desc(sort_column)
    users_query = users_query.order_by(sort_expression)

    return paginate_query(users_query, page=page, limit=limit, skip=skip)

@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_in: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_in.model_dump(exclude_unset=True)
    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password
        
    for field, value in update_data.items():
        setattr(user, field, value)
        
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete currently logged in user")
        
    db.delete(user)
    db.commit()
    return {"detail": "User deleted successfully"}
