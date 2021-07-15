from fastapi import APIRouter

from . import heartbeat

api_router = APIRouter()

api_router.include_router(heartbeat.router, tags=["health"], prefix="/health")

# api_router.include_router(prediction.router, tags=[
#                           "prediction"], prefix="/model")
