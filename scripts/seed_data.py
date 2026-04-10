import sys
import os

# Set working directory to the project root implicitly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from core.database import SessionLocal, engine, Base
from core.security import get_password_hash
from models.admin import User, SystemSetting
from models.pos import Category, Product, Table
from models.customer import Customer
from datetime import date

def seed_data():
    db: Session = SessionLocal()

    try:
        Base.metadata.create_all(bind=engine)

        # 1. Create Admin User
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            hashed_pw = get_password_hash("admin")
            admin_user = User(
                username="admin",
                hashed_password=hashed_pw,
                full_name="System Admin",
                role="admin",
                status="active"
            )
            db.add(admin_user)
            print("Created Admin user (admin / admin)")

        # 2. Create System Settings
        if not db.query(SystemSetting).filter(SystemSetting.key == "SHOP_NAME").first():
            db.add(SystemSetting(key="SHOP_NAME", value="DeepCoffee Flagship", description="Name of the coffee shop"))

        # 3. Create Categories
        if db.query(Category).count() == 0:
            c1 = Category(name="Cà phê máy", sort_order=1)
            c2 = Category(name="Trà trái cây", sort_order=2)
            c3 = Category(name="Bánh ngọt", sort_order=3)
            db.add_all([c1, c2, c3])
            db.commit()  # Commit early to get category IDs

            # 4. Create Products
            p1 = Product(category_id=c1.id, sku="CF01", name="Espresso", price=35000.0)
            p2 = Product(category_id=c1.id, sku="CF02", name="Americano", price=40000.0)
            p3 = Product(category_id=c1.id, sku="CF03", name="Latte", price=55000.0)
            p4 = Product(category_id=c2.id, sku="TE01", name="Trà Đào Cam Sả", price=45000.0)
            p5 = Product(category_id=c2.id, sku="TE02", name="Trà Vải Thiều", price=45000.0)
            p6 = Product(category_id=c3.id, sku="CA01", name="Tiramisu", price=60000.0)
            db.add_all([p1, p2, p3, p4, p5, p6])
            print("Created Categories and Products")

        # 5. Create Tables
        if db.query(Table).count() == 0:
            t1 = Table(name="Tầng 1 - Bàn 1", area="Tầng 1", capacity=4)
            t2 = Table(name="Tầng 1 - Bàn 2", area="Tầng 1", capacity=2)
            t3 = Table(name="Tầng 2 - Sofa 1", area="Tầng 2", capacity=6)
            t4 = Table(name="Sân vườn - VIP", area="Ngoài trời", capacity=8)
            db.add_all([t1, t2, t3, t4])
            print("Created Tables")

        # 6. Create Customers
        if db.query(Customer).count() == 0:
            cus1 = Customer(full_name="Nguyễn Văn A", phone="0987654321", gender="male", birthday=date(1995, 5, 20), note="Khách quen hay uống Americano đá")
            cus2 = Customer(full_name="Trần Thị B", phone="0911222333", gender="female", birthday=date(1998, 10, 15), note="Hay mua bánh Tiramisu")
            db.add_all([cus1, cus2])
            print("Created Sample Customers")

        db.commit()
        print("Database seeding completed gracefully.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting database seeding...")
    seed_data()
