from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from models.pos import Invoice
from models.customer import Customer
from core.config import settings

class LoyaltyService:
    def __init__(self, db: Session):
        self.db = db

    def check_customer_loyalty(self, customer_id: int) -> dict:
        """
        Check if a customer is loyal by satisfying the condition:
        >= X valid invoices in the last Y days.
        """
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return {"qualified": False, "invoice_count_30d": 0, "customer": None}

        # Calculate the date window
        thirty_days_ago = datetime.utcnow() - timedelta(days=settings.LOYALTY_DAYS_WINDOW)

        # Query valid invoices in the given timeframe
        invoice_count = self.db.query(func.count(Invoice.id)).filter(
            and_(
                Invoice.customer_id == customer_id,
                Invoice.invoice_status == "valid",
                Invoice.issued_at >= thirty_days_ago
            )
        ).scalar() or 0

        # Check against rule
        qualified = invoice_count >= settings.LOYALTY_INVOICE_REQUIRED

        return {
            "qualified": qualified,
            "invoice_count_30d": invoice_count,
            "customer": customer
        }
