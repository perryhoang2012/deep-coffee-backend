from core.database import SessionLocal
from models.pos import Invoice
from models.customer import Customer
from models.admin import User
from datetime import datetime, timedelta
from uuid import uuid4

def seed_invoices_direct(customer_id, count=12):
    db = SessionLocal()
    try:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            print(f"Customer {customer_id} not found.")
            return
            
        admin = db.query(User).filter(User.role == "admin").first()
        admin_id = admin.id if admin else 1
        
        print(f"Adding {count} invoices for {customer.full_name}...")
        
        for i in range(count):
            # Spread over the last 15 days
            days_ago = i % 15
            issued_at = datetime.utcnow() - timedelta(days=days_ago)
            
            invoice = Invoice(
                customer_id=customer_id,
                invoice_code=f"AUTO-{customer_id}-{uuid4().hex[:6].upper()}",
                subtotal=50000.0,
                total_amount=50000.0,
                payment_status="paid",
                invoice_status="valid",
                created_by=admin_id,
                issued_at=issued_at
            )
            db.add(invoice)
        
        db.commit()
        print(f"Successfully added {count} invoices.")
        
        # Verify loyalty
        from services.loyalty_service import LoyaltyService
        loyalty = LoyaltyService(db).check_customer_loyalty(customer_id)
        print(f"Loyalty Status: {'QUALIFIED' if loyalty['qualified'] else 'NOT QUALIFIED'}")
        print(f"Orders in 30 days: {loyalty['invoice_count_30d']}")
        
    finally:
        db.close()

if __name__ == "__main__":
    seed_invoices_direct(3)
