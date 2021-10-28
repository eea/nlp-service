from app.core.config import CONCURRENT_REQUEST_PER_WORKER
from app.core.utils import RequestLimiter
from fastapi import APIRouter, Request

from .api import QA_Request, Response

router = APIRouter()

concurrency_limiter = RequestLimiter(CONCURRENT_REQUEST_PER_WORKER)


@router.post("", response_model=Response)
def query(payload: QA_Request, request: Request):
    params = payload.dict()['params']
    if params.get('use_dp'):
        model = request.app.state.dp_qa
    else:
        model = request.app.state.qa

    with concurrency_limiter.run():
        return model.predict(payload)
