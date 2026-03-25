from fastapi import APIRouter
from api.v1.endpoints import auth, users, customers, pos, events

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(customers.router, prefix="/customers", tags=["customers"])
api_router.include_router(pos.router, prefix="/pos", tags=["pos"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
