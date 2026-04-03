from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from core.config import settings


class StorageService:
    def ensure_directories(self):
        settings.STORAGE_PATH.mkdir(parents=True, exist_ok=True)
        settings.FACE_STORAGE_PATH.mkdir(parents=True, exist_ok=True)
        settings.RECOGNITION_STORAGE_PATH.mkdir(parents=True, exist_ok=True)

    def save_customer_face(self, customer_id: int, filename: str, content: bytes) -> str:
        ext = self._safe_extension(filename)
        customer_dir = settings.FACE_STORAGE_PATH / f"customer_{customer_id}"
        customer_dir.mkdir(parents=True, exist_ok=True)
        stored_name = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}{ext}"
        target = customer_dir / stored_name
        target.write_bytes(content)
        return str(target)

    def save_recognition_snapshot(self, camera_id: str, filename: str, content: bytes) -> str:
        date_dir = settings.RECOGNITION_STORAGE_PATH / datetime.utcnow().strftime("%Y-%m-%d")
        date_dir.mkdir(parents=True, exist_ok=True)
        ext = self._safe_extension(filename)
        safe_camera = self._safe_slug(camera_id)
        stored_name = f"{safe_camera}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}{ext}"
        target = date_dir / stored_name
        target.write_bytes(content)
        return str(target)

    def _safe_extension(self, filename: str) -> str:
        ext = Path(filename).suffix.lower()
        return ext if ext in {".jpg", ".jpeg", ".png", ".webp"} else ".jpg"

    def _safe_slug(self, value: str) -> str:
        return "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in value) or "camera"
