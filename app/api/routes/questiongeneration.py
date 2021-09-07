from app.core.config import CONCURRENT_REQUEST_PER_WORKER
from app.core.utils import RequestLimiter
from app.data_models.questiongeneration import (QuestionGenerationRequest,
                                                QuestionGenerationResponse)
from fastapi import APIRouter, Request

router = APIRouter()

concurrency_limiter = RequestLimiter(CONCURRENT_REQUEST_PER_WORKER)


@router.post("/query", response_model=QuestionGenerationResponse)
def query(payload: QuestionGenerationRequest, request: Request):
    model = request.app.state.question_generation_model_b
    with concurrency_limiter.run():
        return model.predict(payload)
