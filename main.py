from http import HTTPStatus
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException
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


def ensure_product_inventory_columns():
    inspector = inspect(engine)
    if not inspector.has_table("products"):
        return

    existing_columns = {column["name"] for column in inspector.get_columns("products")}
    column_statements = {
        "stock_quantity": "ALTER TABLE products ADD COLUMN stock_quantity INTEGER DEFAULT 0 NOT NULL",
        "low_stock_threshold": "ALTER TABLE products ADD COLUMN low_stock_threshold INTEGER DEFAULT 5 NOT NULL",
    }

    with engine.begin() as connection:
        for column_name, statement in column_statements.items():
            if column_name not in existing_columns:
                connection.execute(text(statement))

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)


def build_error_response(
    status_code: int,
    detail: Any,
    *,
    message: str | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    try:
        default_error = HTTPStatus(status_code).phrase
    except ValueError:
        default_error = "Error"

    if message is None:
        message = detail if isinstance(detail, str) and detail else default_error

    return {
        "message": message,
        "status": status_code,
        "error": error or default_error,
        "detail": detail,
    }

static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_origin_regex=settings.BACKEND_CORS_ORIGIN_REGEX,
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


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=build_error_response(exc.status_code, exc.detail),
        headers=getattr(exc, "headers", None),
    )


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(_: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=build_error_response(
            422,
            exc.errors(),
            message="Validation error",
        ),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(
        "Unhandled exception while processing %s %s",
        request.method,
        request.url.path,
        exc_info=exc,
    )
    return JSONResponse(
        status_code=500,
        content=build_error_response(
            500,
            "An unexpected error occurred",
            message="Internal server error",
        ),
    )

@app.on_event("startup")
def startup_event():
    StorageService().ensure_directories()

    if not settings.AUTO_CREATE_TABLES:
        return

    try:
        Base.metadata.create_all(bind=engine)
        ensure_product_inventory_columns()
    except SQLAlchemyError as exc:
        logger.warning("Database is unavailable during startup table creation: %s", exc)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Include WebSocket router
app.include_router(dashboard.router, tags=["websockets"])
