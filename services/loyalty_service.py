from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
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
        if customer_id is None:
            return {
                "qualified": False,
                "invoice_count_30d": 0,
                "invoice_count_period": 0,
                "total_orders": 0,
                "customer": None,
                "invoice_required": settings.LOYAL_CUSTOMER_MIN_ORDERS,
                "days_window": settings.LOYAL_CUSTOMER_PERIOD_DAYS,
            }

        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return {
                "qualified": False,
                "invoice_count_30d": 0,
                "invoice_count_period": 0,
                "total_orders": 0,
                "customer": None,
                "invoice_required": settings.LOYAL_CUSTOMER_MIN_ORDERS,
                "days_window": settings.LOYAL_CUSTOMER_PERIOD_DAYS,
            }

        # Calculate the date window
        period_start = datetime.utcnow() - timedelta(days=settings.LOYAL_CUSTOMER_PERIOD_DAYS)

        # Query valid invoices in the given timeframe
        recent_invoice_count = self.db.query(func.count(Invoice.id)).filter(
            and_(
                Invoice.customer_id == customer_id,
                Invoice.invoice_status == "valid",
                or_(Invoice.payment_status.is_(None), Invoice.payment_status != "refunded"),
                or_(Invoice.invoice_code.is_(None), ~Invoice.invoice_code.ilike("TEST%")),
                Invoice.issued_at >= period_start
            )
        ).scalar() or 0

        total_orders = self.db.query(func.count(Invoice.id)).filter(
            and_(
                Invoice.customer_id == customer_id,
                Invoice.invoice_status == "valid",
                or_(Invoice.payment_status.is_(None), Invoice.payment_status != "refunded"),
                or_(Invoice.invoice_code.is_(None), ~Invoice.invoice_code.ilike("TEST%")),
            )
        ).scalar() or 0

        # Check against rule
        qualified = recent_invoice_count >= settings.LOYAL_CUSTOMER_MIN_ORDERS

        return {
            "qualified": qualified,
            "invoice_count_30d": recent_invoice_count,
            "invoice_count_period": recent_invoice_count,
            "total_orders": total_orders,
            "customer": customer,
            "invoice_required": settings.LOYAL_CUSTOMER_MIN_ORDERS,
            "days_window": settings.LOYAL_CUSTOMER_PERIOD_DAYS,
        }
