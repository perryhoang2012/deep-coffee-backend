from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from core.database import Base
from models.customer import Customer, CustomerFace
from services.customer_face_retention import prune_customer_faces


class CustomerFaceRetentionTests(unittest.TestCase):
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
        test_tmp_root = Path.cwd() / ".test-tmp"
        test_tmp_root.mkdir(exist_ok=True)
        self.temp_dir = tempfile.TemporaryDirectory(dir=test_tmp_root)

    def tearDown(self):
        self.temp_dir.cleanup()
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_prune_keeps_ten_newest_faces_and_removes_old_files(self):
        customer = Customer(full_name="Nguyen Van A")
        self.db.add(customer)
        self.db.flush()

        base_time = datetime(2026, 5, 28, 8, 0, 0)
        created_faces = []
        for index in range(12):
            image_path = Path(self.temp_dir.name) / f"face_{index}.jpg"
            image_path.write_bytes(b"face")
            face = CustomerFace(
                customer_id=customer.id,
                image_path=str(image_path),
                embedding="[]",
                is_primary=False,
                created_at=base_time + timedelta(minutes=index),
            )
            self.db.add(face)
            self.db.flush()
            created_faces.append(face)

        deleted_faces = prune_customer_faces(self.db, customer.id, keep_latest=10)
        self.db.commit()

        remaining_ids = {
            face.id
            for face in self.db.query(CustomerFace)
            .filter(CustomerFace.customer_id == customer.id)
            .all()
        }

        self.assertEqual(len(deleted_faces), 2)
        self.assertEqual(len(remaining_ids), 10)
        self.assertNotIn(created_faces[0].id, remaining_ids)
        self.assertNotIn(created_faces[1].id, remaining_ids)
        self.assertFalse(Path(created_faces[0].image_path).exists())
        self.assertFalse(Path(created_faces[1].image_path).exists())


if __name__ == "__main__":
    unittest.main()
