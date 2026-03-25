# DeepCoffee Backend

Dự án máy chủ quản lý quán Cà phê (POS, Admin) có tích hợp hệ thống nhận diện khách hàng thân thiết và tự động chào đón qua Camera. Dựa trên `Agent_Skill.MD`, Project Backend này được thiết lập bằng **FastAPI**, kết hợp **PostgreSQL** (SQLAlchemy + pg8000) và hệ thống PubSub WebSocket. Phần nhận diện CV/DeepLearning AI sẽ được tích hợp vào sau.

## 🚀 Tính Năng (MVP)
- **Hệ thống POS (Điểm Bán Hàng)**: Tạo/Sửa các Invoices, Products, Bàn và quản lý tình trạng thanh toán.
- **Hệ thống Admin**: Authentication (đăng nhập) nhân viên, Phân quyền người dùng, Dashboard Dashboard khách hàng.
- **Loyalty & Greeting Engine**: Tự động tính toán lượng giao dịch POS (>= 10 Invoices trong 30 ngày gần nhất) để xác định Khách Quen (Loyal Customer) và chống tạo lời chào (greeting) trùng lặp với thời gian Cooldown.
- **WebSocket Dashboard Realtime**: Gửi sự kiện realtime ngay khi tính toán module Greeting phát hành sự kiện.

## 📁 Cấu Trúc Khung Kiến Trúc
```text
DeepCoffee_BE/
├── main.py                    # Khởi tạo instance của FastAPI (App Entrypoint)
├── requirements.txt           # Phiên bản thư viện Pip (Starlette, SQLAlchemy...)
├── docker-compose.yml         # Container DB của PostgreSQL
├── core/                      # Các Configurations, DB Session và Authentication Setup
├── models/                    # Khai báo cấu trúc Bảng của CSDL (SQLAlchemy ORM)
├── schemas/                   # Pydantic Objects Validation in/out REST_API
├── api/                       # Định tuyến URL (Endpoints Router & Dependencies)
│   ├── v1/endpoints           (Auth, Users, POS, Customers, Events)
│   └── websockets             (Realtime Dashboard Connection Manager)
└── services/                  # Business Logic Engine
    ├── loyalty_service.py     # Check <= 30 Days & >= 10 Bills
    └── greeting_service.py    # Nhận Payload Camera -> Check Loyalty -> Phát Event 
```

## ⚙️ Hướng Dẫn Cài Đặt và Khởi Chạy Local

**1. Khởi Động Base Database qua Docker:**
```bash
docker-compose up -d
```

**2. Cài Đặt Môi Trường Ảo Python (.venv):**
Hệ thống sử dụng Driver Python thuần `pg8000` để vượt qua lỗi thiếu `pg_config` của `psycopg2` trên MacOS.
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**3. Test Local FastAPI Server**
Chạy ứng dụng với hot-reload Uvicorn:
```bash
uvicorn main:app --reload
```
Sau đó truy cập trang Swagger Test: [http://localhost:8000/docs](http://localhost:8000/docs)
