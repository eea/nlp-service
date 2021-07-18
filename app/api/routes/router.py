from fastapi import APIRouter

from . import heartbeat, qa, search

api_router = APIRouter()

api_router.include_router(heartbeat.router, tags=["health"], prefix="/health")
api_router.include_router(qa.router, tags=["qa"], prefix="/qa")
api_router.include_router(search.router, tags=["qa"], prefix="/search")

# api_router.include_router(prediction.router, tags=[
#                           "prediction"], prefix="/model")
