import json
import math
from typing import Iterable, Optional

from sqlalchemy.orm import Session, joinedload

from core.config import settings
from models.customer import CustomerFace


class FaceRecognitionService:
    def __init__(self, db: Session):
        self.db = db

    def match_customer(self, embedding: Optional[Iterable[float]]) -> dict:
        if not embedding:
            return {"customer": None, "face": None, "confidence": None}

        query_embedding = [float(value) for value in embedding]
        best_face = None
        best_score = -1.0

        faces = (
            self.db.query(CustomerFace)
            .options(joinedload(CustomerFace.customer))
            .all()
        )

        for face in faces:
            stored_embedding = self._parse_embedding(face.embedding)
            if not stored_embedding:
                continue

            score = self._cosine_similarity(query_embedding, stored_embedding)
            if score > best_score:
                best_score = score
                best_face = face

        if not best_face or best_score < settings.FACE_MATCH_THRESHOLD:
            return {"customer": None, "face": None, "confidence": best_score if best_score >= 0 else None}

        return {
            "customer": best_face.customer,
            "face": best_face,
            "confidence": round(best_score, 4),
        }

    def _parse_embedding(self, raw_embedding: Optional[str]) -> Optional[list[float]]:
        if not raw_embedding:
            return None

        try:
            data = json.loads(raw_embedding)
            if isinstance(data, list):
                return [float(value) for value in data]
        except json.JSONDecodeError:
            pass

        try:
            return [float(value.strip()) for value in raw_embedding.split(",") if value.strip()]
        except ValueError:
            return None

    def _cosine_similarity(self, left: list[float], right: list[float]) -> float:
        if len(left) != len(right) or not left:
            return -1.0

        dot_product = sum(a * b for a, b in zip(left, right))
        left_norm = math.sqrt(sum(value * value for value in left))
        right_norm = math.sqrt(sum(value * value for value in right))
        if left_norm == 0 or right_norm == 0:
            return -1.0

        return dot_product / (left_norm * right_norm)
