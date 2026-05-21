from core.database import SessionLocal
from models.customer import CustomerFace

def count_faces():
    db = SessionLocal()
    try:
        count = db.query(CustomerFace).count()
        print(f"Total faces in database: {count}")
        if count > 0:
            faces = db.query(CustomerFace).limit(5).all()
            for f in faces:
                print(f"Face ID: {f.id}, Customer ID: {f.customer_id}, Path: {f.image_path}")
    finally:
        db.close()

if __name__ == "__main__":
    count_faces()
