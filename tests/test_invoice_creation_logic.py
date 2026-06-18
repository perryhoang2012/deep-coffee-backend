import unittest
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from core.database import Base
from models.admin import User
from models.pos import Product, Table, Invoice
from schemas.pos import InvoiceCreate, InvoiceItemCreate, PaymentCreate
from api.v1.endpoints.pos import create_invoice


class InvoiceCreationLogicTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )
        Base.metadata.create_all(bind=self.engine)

        self.db = self.SessionLocal()
        self.current_user = User(
            id=1,
            username="admin",
            full_name="Admin",
            hashed_password="hash",
            role="admin",
            status="active",
        )

        # Seed initial data
        self.product1 = Product(
            id=1,
            category_id=1,
            sku="TIRA",
            name="Tiramisu",
            price=60000,
            stock_quantity=10,
            status="active",
        )
        self.product2 = Product(
            id=2,
            category_id=1,
            sku="AME",
            name="Americano",
            price=40000,
            stock_quantity=5,
            status="active",
        )
        self.table = Table(
            id=1,
            name="Table 1",
            status="occupied",
            capacity=4,
        )
        self.db.add_all([self.product1, self.product2, self.table])
        self.db.commit()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_create_invoice_successfully_deducts_stock_and_releases_table(self):
        invoice_in = InvoiceCreate(
            customer_id=None,
            table_id=1,
            subtotal=100000,
            discount_amount=0,
            surcharge_amount=0,
            total_amount=100000,
            payment_status="paid",
            invoice_status="valid",
            created_by=None,  # verify created_by is optional
            items=[
                InvoiceItemCreate(
                    product_id=1,
                    product_name_snapshot="Tiramisu",
                    quantity=1,
                    unit_price=60000,
                    line_total=60000,
                ),
                InvoiceItemCreate(
                    product_id=2,
                    product_name_snapshot="Americano",
                    quantity=2,
                    unit_price=40000,
                    line_total=80000,
                ),
            ],
            payments=[
                PaymentCreate(
                    method="cash",
                    amount=100000,
                )
            ]
        )

        # Act
        created_invoice = create_invoice(
            invoice_in=invoice_in,
            db=self.db,
            current_user=self.current_user,
        )

        # Assert Invoice table_id and created_by
        self.assertEqual(created_invoice.table_id, 1)
        self.assertEqual(created_invoice.created_by, self.current_user.id)
        
        # Verify database record
        db_invoice = self.db.query(Invoice).filter(Invoice.id == created_invoice.id).first()
        self.assertIsNotNone(db_invoice)
        self.assertEqual(db_invoice.table_id, 1)
        self.assertEqual(db_invoice.created_by, self.current_user.id)

        # Assert stock deduction
        db_product1 = self.db.query(Product).filter(Product.id == 1).first()
        db_product2 = self.db.query(Product).filter(Product.id == 2).first()
        self.assertEqual(db_product1.stock_quantity, 9)  # 10 - 1
        self.assertEqual(db_product2.stock_quantity, 3)  # 5 - 2

        # Assert table is released (available)
        db_table = self.db.query(Table).filter(Table.id == 1).first()
        self.assertEqual(db_table.status, "available")

    def test_create_invoice_unpaid_does_not_release_table(self):
        invoice_in = InvoiceCreate(
            customer_id=None,
            table_id=1,
            subtotal=100000,
            discount_amount=0,
            surcharge_amount=0,
            total_amount=100000,
            payment_status="unpaid",
            invoice_status="valid",
            created_by=None,
            items=[],
            payments=[]
        )

        # Act
        create_invoice(
            invoice_in=invoice_in,
            db=self.db,
            current_user=self.current_user,
        )

        # Assert table is still occupied
        db_table = self.db.query(Table).filter(Table.id == 1).first()
        self.assertEqual(db_table.status, "occupied")


if __name__ == "__main__":
    unittest.main()
