import logging

from app.api.search.api import SearchRequest
from app.core.config import CONCURRENT_REQUEST_PER_WORKER
from app.core.utils import RequestLimiter
from fastapi import APIRouter, Request

router = APIRouter()

logger = logging.getLogger(__name__)

concurrency_limiter = RequestLimiter(CONCURRENT_REQUEST_PER_WORKER)


@router.post("")
def post_querysearch(payload: SearchRequest, request: Request):
    component = request.app.state.querysearch.component

    with concurrency_limiter.run():
        response = component.predict(payload)

    return response


post_querysearch.__doc__ = """ """
