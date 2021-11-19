from app.core.config import CONCURRENT_REQUEST_PER_WORKER
from app.core.utils import RequestLimiter
from fastapi import APIRouter, Request

from .api import TikaRequest, TikaResponse

router = APIRouter()

concurrency_limiter = RequestLimiter(CONCURRENT_REQUEST_PER_WORKER)


@router.post("", response_model=TikaResponse)
def query(payload: TikaRequest, request: Request):
    model = request.app.state.tika_model

    with concurrency_limiter.run():
        return model.predict(payload)
