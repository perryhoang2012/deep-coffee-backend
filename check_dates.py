from core.database import SessionLocal
from models.customer import Customer

def check_dates():
    db = SessionLocal()
    try:
        c = db.query(Customer).filter(Customer.id == 3).first()
        if c:
            print(f"Customer 3: {c.full_name}, Created at: {c.created_at}")
    finally:
        db.close()

if __name__ == "__main__":
    check_dates()
