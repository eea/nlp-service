from app.core.config import CONCURRENT_REQUEST_PER_WORKER
from app.core.utils import RequestLimiter
from fastapi import APIRouter, Request

from .api import SpacyNERRequest, SpacyNERResponse

router = APIRouter()

concurrency_limiter = RequestLimiter(CONCURRENT_REQUEST_PER_WORKER)


@router.post("", response_model=SpacyNERResponse)
def query(payload: SpacyNERRequest, request: Request):
    model = request.app.state.spacy_ner_model

    with concurrency_limiter.run():
        return model.predict(payload)
