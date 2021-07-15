import json
import time

from fastapi import APIRouter
from loguru import logger

from app.core.config import CONCURRENT_REQUEST_PER_WORKER
from app.core.utils import RequestLimiter
from app.data_models.search import Request, Response

router = APIRouter()


concurrency_limiter = RequestLimiter(CONCURRENT_REQUEST_PER_WORKER)


def _process_request(pipeline, request):
    start_time = time.time()

    filters = {}
    if request.filters:
        # put filter values into a list and remove filters with null value
        for key, values in request.filters.items():
            if values is None:
                continue
            if not isinstance(values, list):
                values = [values]
            filters[key] = values

    result = pipeline.run(
        query=request.query,
        filters=filters,
        top_k_retriever=request.top_k_retriever,
        top_k_reader=request.top_k_reader,
    )

    end_time = time.time()
    info = {
        "request": request.dict(),
        "response": result,
        "time": f"{(end_time - start_time):.2f}",
    }
    logger.info(json.dumps(info))

    return result


@router.post("/query", response_model=Response)
def query(request: Request):
    pipeline = request.app.state.models.qa
    with concurrency_limiter.run():
        result = _process_request(pipeline, request)
        return result
