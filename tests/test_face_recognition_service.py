import json
import math
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from core.database import Base
from models.customer import Customer, CustomerFace
from services.face_recognition_service import FaceRecognitionService


class FaceRecognitionServiceTests(unittest.TestCase):
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

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_rejects_weak_face_similarity_as_unknown_customer(self):
        customer = Customer(full_name="Hoang Van Huynh")
        stored_embedding = [0.75, math.sqrt(1 - 0.75**2)]
        customer.faces.append(
            CustomerFace(
                embedding=json.dumps(stored_embedding),
                is_primary=True,
            ),
        )
        self.db.add(customer)
        self.db.commit()

        result = FaceRecognitionService(self.db).match_customer([1.0, 0.0])

        self.assertIsNone(result["customer"])
        self.assertIsNone(result["face"])
        self.assertAlmostEqual(result["confidence"], 0.75, places=4)

    def test_accepts_high_confidence_face_similarity(self):
        customer = Customer(full_name="Hoang Van Huynh")
        stored_embedding = [0.85, math.sqrt(1 - 0.85**2)]
        customer.faces.append(
            CustomerFace(
                embedding=json.dumps(stored_embedding),
                is_primary=True,
            ),
        )
        self.db.add(customer)
        self.db.commit()

        result = FaceRecognitionService(self.db).match_customer([1.0, 0.0])

        self.assertEqual(result["customer"].full_name, "Hoang Van Huynh")
        self.assertAlmostEqual(result["confidence"], 0.85, places=4)


if __name__ == "__main__":
    unittest.main()
