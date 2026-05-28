import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from core.database import Base
from models.admin import User
from schemas.pos import ProductCreate, ProductResponse


class InventorySettingsTests(unittest.TestCase):
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

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_product_schema_accepts_stock_fields(self):
        product = ProductCreate(
            category_id=1,
            sku="CF01",
            name="Espresso",
            price=35000,
            stock_quantity=12,
            low_stock_threshold=3,
        )

        self.assertEqual(product.stock_quantity, 12)
        self.assertEqual(product.low_stock_threshold, 3)

    def test_product_response_defaults_stock_fields(self):
        product = ProductResponse(
            id=1,
            category_id=1,
            sku="CF01",
            name="Espresso",
            price=35000,
            status="active",
            image_url=None,
            stock_quantity=0,
            low_stock_threshold=5,
            created_at="2026-05-27T00:00:00",
            updated_at="2026-05-27T00:00:00",
        )

        self.assertEqual(product.stock_quantity, 0)
        self.assertEqual(product.low_stock_threshold, 5)

    def test_settings_can_be_upserted_and_listed(self):
        from api.v1.endpoints.settings import (
            SettingUpsert,
            list_settings,
            upsert_setting,
        )

        upsert_response = upsert_setting(
            key="SHOP_NAME",
            payload=SettingUpsert(
                value="DeepCoffee Flagship",
                description="Name of the coffee shop",
            ),
            db=self.db,
            current_user=self.current_user,
        )
        self.assertEqual(upsert_response.key, "SHOP_NAME")
        self.assertEqual(upsert_response.value, "DeepCoffee Flagship")

        list_response = list_settings(db=self.db, current_user=self.current_user)
        self.assertEqual(len(list_response), 1)
        self.assertEqual(list_response[0].key, "SHOP_NAME")


if __name__ == "__main__":
    unittest.main()
