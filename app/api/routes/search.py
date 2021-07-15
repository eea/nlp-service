import json
import logging
import time
from pathlib import Path

from fastapi import APIRouter
from haystack import Pipeline
from rest_api.controller.utils import RequestLimiter

from app.core.config import (
    CONCURRENT_REQUEST_PER_WORKER,
    LOG_LEVEL,
    PIPELINE_YAML_PATH,
    QUERY_PIPELINE_NAME,
)
from app.data_models.search import Request, Response

# from pydantic import BaseModel
# from typing import Any, Dict, List, Optional, Union


logging.getLogger("haystack").setLevel(LOG_LEVEL)
logger = logging.getLogger("haystack")

router = APIRouter()


PIPELINE = Pipeline.load_from_yaml(
    Path(PIPELINE_YAML_PATH), pipeline_name=QUERY_PIPELINE_NAME
)
logger.info(f"Loaded pipeline nodes: {PIPELINE.graph.nodes.keys()}")
concurrency_limiter = RequestLimiter(CONCURRENT_REQUEST_PER_WORKER)


@router.post("/query", response_model=Response)
def query(request: Request):
    with concurrency_limiter.run():
        result = _process_request(PIPELINE, request)
        return result


def _process_request(pipeline, request) -> Response:
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
    logger.info(
        json.dumps(
            {
                "request": request.dict(),
                "response": result,
                "time": f"{(end_time - start_time):.2f}",
            }
        )
    )

    return result
