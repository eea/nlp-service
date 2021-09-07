from app.core.config import CONCURRENT_REQUEST_PER_WORKER
from app.core.utils import RequestLimiter
from fastapi import APIRouter, Request

from .api import SimilarityRequest, SimilarityResponse

router = APIRouter()

concurrency_limiter = RequestLimiter(CONCURRENT_REQUEST_PER_WORKER)


@router.post("/query", response_model=SimilarityResponse)
def query(payload: SimilarityRequest, request: Request):
    model = request.app.state.similarity_model

    with concurrency_limiter.run():
        return model.predict(payload)
