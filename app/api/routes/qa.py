import logging
from pathlib import Path

from app.core.config import (CONCURRENT_REQUEST_PER_WORKER, LOG_LEVEL,
                             PIPELINE_YAML_PATH, QUERY_PIPELINE_NAME)
from app.core.utils import RequestLimiter
from app.data_models.search import Request, Response
from fastapi import APIRouter
from haystack import Pipeline

logging.getLogger("haystack").setLevel(LOG_LEVEL)
logger = logging.getLogger("haystack")

router = APIRouter()


PIPELINE = Pipeline.load_from_yaml(
    Path(PIPELINE_YAML_PATH), pipeline_name=QUERY_PIPELINE_NAME)
logger.info(f"Loaded pipeline nodes: {PIPELINE.graph.nodes.keys()}")
concurrency_limiter = RequestLimiter(CONCURRENT_REQUEST_PER_WORKER)


@router.post("/query", response_model=Response)
def query(request: Request):
    with concurrency_limiter.run():
        result = _process_request(PIPELINE, request)
        return result

# import json
# import time
# from app.services.qa_model import QAModel
