from app.core.config import CONCURRENT_REQUEST_PER_WORKER
from app.core.utils import RequestLimiter
from fastapi import APIRouter, Request

from .api import QuestionRequest, QuestionResponse

router = APIRouter()

concurrency_limiter = RequestLimiter(CONCURRENT_REQUEST_PER_WORKER)


@router.post("", response_model=QuestionResponse)
def query(payload: QuestionRequest, request: Request):
    model = request.app.state.QUESTION_CLASSIFIER
    with concurrency_limiter.run():
        return model.predict(payload)
