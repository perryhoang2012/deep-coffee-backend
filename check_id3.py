from core.database import SessionLocal
from models.customer import Customer, CustomerFace

def check_customer():
    db = SessionLocal()
    try:
        customer = db.query(Customer).filter(Customer.id == 3).first()
        if not customer:
            print("Customer 3 not found in database.")
            return
        
        print(f"Customer 3 found: {customer.full_name}")
        
        faces = db.query(CustomerFace).filter(CustomerFace.customer_id == 3).all()
        print(f"Customer 3 has {len(faces)} faces in database.")
        for face in faces:
            print(f"  - Face ID: {face.id}, Path: {face.image_path}, Primary: {face.is_primary}")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_customer()
