from apis.v1 import route_user
from apis.v1 import route_session
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(route_user.router, prefix="/auth", tags=["authentication"])
api_router.include_router(route_session.router, prefix="/session", tags=["YouTube"])