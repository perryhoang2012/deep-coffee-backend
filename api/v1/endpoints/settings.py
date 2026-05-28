from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.dependencies import get_current_active_user
from core.database import get_db
from models.admin import SystemSetting, User
from schemas.admin import (
    SystemSettingCreate,
    SystemSettingResponse,
    SystemSettingUpdate,
    SystemSettingUpsert,
)

router = APIRouter()


SettingUpsert = SystemSettingUpsert


@router.get("", response_model=List[SystemSettingResponse])
def list_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return db.query(SystemSetting).order_by(SystemSetting.key.asc()).all()


@router.post("", response_model=SystemSettingResponse)
def create_setting(
    payload: SystemSettingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    existing = db.query(SystemSetting).filter(SystemSetting.key == payload.key).first()
    if existing:
        raise HTTPException(status_code=409, detail="Setting already exists")

    setting = SystemSetting(**payload.model_dump())
    db.add(setting)
    db.commit()
    db.refresh(setting)
    return setting


@router.get("/{key}", response_model=SystemSettingResponse)
def get_setting(
    key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting


@router.put("/{key}", response_model=SystemSettingResponse)
def upsert_setting(
    key: str,
    payload: SystemSettingUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    if not setting:
        setting = SystemSetting(
            key=key,
            value=payload.value,
            description=payload.description,
        )
        db.add(setting)
    else:
        setting.value = payload.value
        setting.description = payload.description

    db.commit()
    db.refresh(setting)
    return setting


@router.patch("/{key}", response_model=SystemSettingResponse)
def update_setting(
    key: str,
    payload: SystemSettingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(setting, field, value)

    db.commit()
    db.refresh(setting)
    return setting


@router.delete("/{key}")
def delete_setting(
    key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")

    db.delete(setting)
    db.commit()
    return {"detail": "Setting deleted successfully"}
