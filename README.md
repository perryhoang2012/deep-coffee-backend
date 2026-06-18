# DeepCoffee Backend

## Project Structure

```text
DeepCoffee_BE/
├── main.py                    # FastAPI entrypoint
├── requirements.txt           # Python dependencies
├── docker-compose.yml         # PostgreSQL service
├── core/                      # Configuration, database, and security
├── models/                    # SQLAlchemy models
├── schemas/                   # Pydantic schemas
├── api/                       # REST API and WebSocket routers
│   ├── v1/endpoints           # Auth, users, POS, customers, events
│   └── websockets             # Realtime dashboard connection manager
└── services/                  # Business logic
    ├── loyalty_service.py
    ├── greeting_service.py
    └── recognition_service.py
```

## Setup

**1. Start PostgreSQL with Docker:**

```bash
docker-compose up -d
```

**2. Create a virtual environment and install dependencies:**

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
.\.venv\Scripts\pip.exe install -r requirements.txt
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**3. Initialize the database and seed sample data:**

macOS / Linux or Git Bash on Windows:

```bash
bash scripts/set_up.sh
```

Windows PowerShell:

```powershell
.\.venv\Scripts\activate
$env:PYTHONPATH = "."
python scripts/seed_data.py
```

**4. Run the FastAPI server:**

Windows PowerShell:

```powershell
.\.venv\Scripts\uvicorn.exe main:app --reload
```

macOS / Linux:

```bash
source .venv/bin/activate
uvicorn main:app --reload
```

## API Documentation

Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
