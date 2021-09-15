from app.core.config import CONCURRENT_REQUEST_PER_WORKER
from app.core.utils import RequestLimiter
from fastapi import APIRouter, Request

from .api import EmbeddingRequest, EmbeddingResponse

router = APIRouter()

concurrency_limiter = RequestLimiter(CONCURRENT_REQUEST_PER_WORKER)


@router.post("", response_model=EmbeddingResponse)
def query(payload: EmbeddingRequest, request: Request):
    model = request.app.state.embedding_model

    with concurrency_limiter.run():
        return model.predict(payload)
