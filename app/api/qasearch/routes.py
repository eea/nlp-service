import logging

from app.api.search.api import SearchRequest
from app.core.config import CONCURRENT_REQUEST_PER_WORKER
from app.core.utils import RequestLimiter
from fastapi import APIRouter, Request

router = APIRouter()

logger = logging.getLogger(__name__)

concurrency_limiter = RequestLimiter(CONCURRENT_REQUEST_PER_WORKER)


def remix(search_response, qa_response):
    res = {}
    res.update(search_response)
    res.update(qa_response)

    return res


@router.post("")
def post_querysearch(payload: SearchRequest, request: Request):
    component = request.app.state.querysearch.component

    body = payload.dict()
    use_dp = body["params"].pop("use_dp", False)
    body.update(body.get("params", {}) or {})
    source = body.pop("source", None)

    # pydantic doesn't like fields with _underscore in beginning?
    # See https://github.com/samuelcolvin/pydantic/issues/288 for possible fixes
    if source:
        body["_source"] = source

    with concurrency_limiter.run():
        search_pipeline = getattr(request.app.state, component.search_pipeline)
        search_response = search_pipeline.predict(body)

        qa_pipeline = getattr(request.app.state, component.qa_pipeline, None)

        if qa_pipeline and body.get("size", 0):
            # import pdb
            #
            # pdb.set_trace()
            qa_response = qa_pipeline.predict(body)
        else:
            qa_response = {}

    response = remix(search_response, qa_response)

    return response


post_querysearch.__doc__ = """ """
