import json
import time

from app.core.config import CONCURRENT_REQUEST_PER_WORKER
from app.core.utils import RequestLimiter
from app.data_models.qa import QA_Request, Response
from fastapi import APIRouter, Request
from loguru import logger

router = APIRouter()


concurrency_limiter = RequestLimiter(CONCURRENT_REQUEST_PER_WORKER)


@router.post("/query", response_model=Response)
def query(payload: QA_Request, request: Request):
    model = request.app.state.qa
    with concurrency_limiter.run():
        return model.predict(payload)
