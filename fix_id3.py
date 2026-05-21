import json
from core.database import SessionLocal
from models.customer import CustomerFace
from services.vision_service import VisionService
from pathlib import Path

def fix_id3():
    db = SessionLocal()
    try:
        # Check if already has face
        existing = db.query(CustomerFace).filter(CustomerFace.customer_id == 3).first()
        if existing:
            print("Customer 3 already has a face in DB.")
            return

        # Find a file
        face_dir = Path("storage/faces/customer_3")
        files = list(face_dir.glob("*.jpg"))
        if not files:
            print("No files found in storage/faces/customer_3")
            return
        
        target_file = files[0]
        print(f"Registering {target_file} for Customer 3...")
        
        # Extract embedding
        image_bytes = target_file.read_bytes()
        vision_result = VisionService().extract_face_embedding(image_bytes)
        
        if not vision_result["success"]:
            print(f"Failed to extract face from {target_file}: {vision_result.get('reason')}")
            return
            
        db_face = CustomerFace(
            customer_id=3,
            image_path=str(target_file),
            embedding=json.dumps(vision_result["embedding"]),
            is_primary=True
        )
        db.add(db_face)
        db.commit()
        print("Success! Customer 3 now has a face registered in the database.")
        
    finally:
        db.close()

if __name__ == "__main__":
    fix_id3()
