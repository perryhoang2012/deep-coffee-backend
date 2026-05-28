from pathlib import Path
from typing import List

from sqlalchemy.orm import Session

from models.customer import CustomerFace

MAX_CUSTOMER_FACE_IMAGES = 10


def prune_customer_faces(
    db: Session,
    customer_id: int,
    keep_latest: int = MAX_CUSTOMER_FACE_IMAGES,
) -> List[CustomerFace]:
    keep_latest = max(1, keep_latest)
    db.flush()

    faces = (
        db.query(CustomerFace)
        .filter(CustomerFace.customer_id == customer_id)
        .order_by(CustomerFace.created_at.desc(), CustomerFace.id.desc())
        .all()
    )
    stale_faces = faces[keep_latest:]

    for face in stale_faces:
        image_path = face.image_path
        db.delete(face)
        if image_path:
            try:
                Path(image_path).unlink(missing_ok=True)
            except OSError:
                pass

    return stale_faces
