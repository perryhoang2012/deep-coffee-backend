import unittest
from datetime import datetime

from schemas.pos import (
    CategoryResponse,
    InvoiceCreate,
    OrderCreate,
    ProductResponse,
    TableResponse,
)


class PosStatusNormalizationTests(unittest.TestCase):
    def test_product_response_normalizes_legacy_stock_status_to_english(self):
        product = ProductResponse(
            id=1,
            category_id=1,
            sku="CF01",
            name="Espresso",
            price=35000,
            stock_quantity=0,
            low_stock_threshold=5,
            status="het hang",
            image_url=None,
            created_at=datetime(2026, 5, 28, 0, 0, 0),
            updated_at=datetime(2026, 5, 28, 0, 0, 0),
        )

        self.assertEqual(product.status, "out_of_stock")

    def test_category_response_normalizes_vietnamese_status_to_english(self):
        category = CategoryResponse(
            id=1,
            name="Coffee",
            status="khong hoat dong",
            sort_order=0,
            created_at=datetime(2026, 5, 28, 0, 0, 0),
            updated_at=datetime(2026, 5, 28, 0, 0, 0),
        )

        self.assertEqual(category.status, "inactive")

    def test_table_response_normalizes_vietnamese_status_to_english(self):
        table = TableResponse(
            id=1,
            name="A1",
            area="Ground",
            status="co khach",
            capacity=4,
            created_at=datetime(2026, 5, 28, 0, 0, 0),
            updated_at=datetime(2026, 5, 28, 0, 0, 0),
        )

        self.assertEqual(table.status, "occupied")

    def test_order_and_invoice_inputs_normalize_vietnamese_status_to_english(self):
        order = OrderCreate(table_id=1, customer_id=None, order_status="dang xu ly", created_by=1)
        invoice = InvoiceCreate(
            customer_id=None,
            subtotal=100000,
            discount_amount=0,
            surcharge_amount=0,
            total_amount=100000,
            payment_status="da thanh toan",
            invoice_status="da huy",
            created_by=1,
            items=[],
            payments=[],
        )

        self.assertEqual(order.order_status, "processing")
        self.assertEqual(invoice.payment_status, "paid")
        self.assertEqual(invoice.invoice_status, "cancelled")


if __name__ == "__main__":
    unittest.main()
