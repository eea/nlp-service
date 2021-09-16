from app.core.config import CONCURRENT_REQUEST_PER_WORKER
from app.core.utils import RequestLimiter
from fastapi import APIRouter, Request

from .api import ZeroShotRequest, ZeroShotResponse

router = APIRouter()

concurrency_limiter = RequestLimiter(CONCURRENT_REQUEST_PER_WORKER)


@router.post("", response_model=ZeroShotResponse)
def query(payload: ZeroShotRequest, request: Request):
    model = request.app.state.zeroshot_classifier_model

    with concurrency_limiter.run():
        return model.predict(payload)
