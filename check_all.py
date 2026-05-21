from core.database import SessionLocal
from models.customer import Customer, CustomerFace

def check_all():
    db = SessionLocal()
    try:
        customers = db.query(Customer).all()
        print(f"Found {len(customers)} customers.")
        for c in customers:
            faces = db.query(CustomerFace).filter(CustomerFace.customer_id == c.id).all()
            print(f"Customer {c.id}: {c.full_name}, {len(faces)} faces.")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_all()
