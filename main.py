from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import SQLAlchemyError
import logging
from pathlib import Path

from core.config import settings
from core.database import engine, Base
from api.v1.api import api_router
from api.v1.websockets import dashboard
from services.storage_service import StorageService
import models.admin  # noqa: F401
import models.customer  # noqa: F401
import models.event  # noqa: F401
import models.pos  # noqa: F401

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Change this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Welcome to DeepCoffee Backend"}

@app.get("/face-test", include_in_schema=False)
def face_test_page():
    return FileResponse(static_dir / "face-test.html")

@app.on_event("startup")
def startup_event():
    StorageService().ensure_directories()

    if not settings.AUTO_CREATE_TABLES:
        return

    try:
        Base.metadata.create_all(bind=engine)
    except SQLAlchemyError as exc:
        logger.warning("Database is unavailable during startup table creation: %s", exc)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Include WebSocket router
app.include_router(dashboard.router, tags=["websockets"])
