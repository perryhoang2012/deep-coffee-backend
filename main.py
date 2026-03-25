from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.database import engine, Base
from api.v1.api import api_router
from api.v1.websockets import dashboard

# Create database tables (Not recommended for prod if using Alembic, but good for local dev)
Base.metadata.create_all(bind=engine)
from core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

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

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Include WebSocket router
app.include_router(dashboard.router, tags=["websockets"])
