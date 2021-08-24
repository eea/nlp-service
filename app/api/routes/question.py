from app.core.config import CONCURRENT_REQUEST_PER_WORKER
from app.core.utils import RequestLimiter
from app.data_models.question import QuestionRequest, QuestionResponse
from fastapi import APIRouter, Request

router = APIRouter()

concurrency_limiter = RequestLimiter(CONCURRENT_REQUEST_PER_WORKER)


@router.post("/query", response_model=QuestionResponse)
def query(payload: QuestionRequest, request: Request):
    model = request.app.state.QUESTION_CLASSIFIER
    with concurrency_limiter.run():
        return model.predict(payload)
