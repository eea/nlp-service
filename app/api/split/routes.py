from app.core.config import CONCURRENT_REQUEST_PER_WORKER
from app.core.utils import RequestLimiter
from fastapi import APIRouter, Request

from .api import SplitRequest, SplitResponse

router = APIRouter()

concurrency_limiter = RequestLimiter(CONCURRENT_REQUEST_PER_WORKER)


@router.post("", response_model=SplitResponse)
def query(payload: SplitRequest, request: Request):

    model = request.app.state.split_model

    with concurrency_limiter.run():
        return model.predict(payload)
