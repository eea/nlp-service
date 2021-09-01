from app.core.config import CONCURRENT_REQUEST_PER_WORKER
from app.core.utils import RequestLimiter
from app.data_models.preprocess import PreprocessRequest, Response
from fastapi import APIRouter, Request

router = APIRouter()

concurrency_limiter = RequestLimiter(CONCURRENT_REQUEST_PER_WORKER)


@router.post("/preprocess", response_model=Response)
def preprocess(payload: PreprocessRequest, request: Request):
    return
