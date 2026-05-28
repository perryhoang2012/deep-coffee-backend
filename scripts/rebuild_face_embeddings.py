import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.database import SessionLocal
from models.customer import CustomerFace
from services.vision_service import VisionService


def rebuild_face_embeddings() -> None:
    db = SessionLocal()
    vision_service = VisionService()
    updated_count = 0
    skipped_count = 0

    try:
        faces = db.query(CustomerFace).order_by(CustomerFace.id.asc()).all()
        for face in faces:
            if not face.image_path:
                skipped_count += 1
                print(f"skip face_id={face.id}: missing image_path")
                continue

            image_path = Path(face.image_path)
            if not image_path.exists():
                skipped_count += 1
                print(f"skip face_id={face.id}: file not found {image_path}")
                continue

            result = vision_service.extract_face_embedding(image_path.read_bytes())
            if not result.get("success"):
                skipped_count += 1
                print(
                    "skip "
                    f"face_id={face.id}: {result.get('reason')} "
                    f"{result.get('message') or ''}".strip()
                )
                continue

            face.embedding = json.dumps(result["embedding"])
            updated_count += 1
            print(
                f"updated face_id={face.id} customer_id={face.customer_id} "
                f"model={result.get('embedding_model', 'unknown')}"
            )

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    print(f"done updated={updated_count} skipped={skipped_count}")


if __name__ == "__main__":
    rebuild_face_embeddings()
