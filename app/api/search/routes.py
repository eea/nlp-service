from app.core.config import CONCURRENT_REQUEST_PER_WORKER
from app.core.utils import RequestLimiter
from fastapi import APIRouter, Request

from .api import SearchRequest  # , SearchResponse

router = APIRouter()

concurrency_limiter = RequestLimiter(CONCURRENT_REQUEST_PER_WORKER)


@router.post("")
def query(payload: SearchRequest, request: Request):
    model = request.app.state.search
    with concurrency_limiter.run():
        result = model.predict(payload)
        return result
