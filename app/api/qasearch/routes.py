import logging

from app.api.search.api import SearchRequest
from app.core.config import CONCURRENT_REQUEST_PER_WORKER
from app.core.elasticsearch import get_search_term
from app.core.utils import RequestLimiter
from fastapi import APIRouter, Request

from .api import QASearchResponse

router = APIRouter()

logger = logging.getLogger(__name__)

concurrency_limiter = RequestLimiter(CONCURRENT_REQUEST_PER_WORKER)


def remix(search_response, qa_response):
    res = {}
    res.update(search_response)
    res.update(qa_response)

    fields = ["elasticsearch_result", "documents", "params", "highlight"]

    for field in fields:
        res.pop(field, None)

    return res


@router.post("")  # , response_model=QASearchResponse
def post_querysearch(payload: SearchRequest, request: Request):
    component = request.app.state.querysearch.component
    excluded_meta_data = component.excluded_meta_data

    body = payload.dict()
    # use_dp = body.get("params", {}).pop("use_dp", False)
    body.update(body.get("params", {}) or {})
    source = body.pop("source", None)

    # pydantic doesn't like fields with _underscore in beginning?
    # See https://github.com/samuelcolvin/pydantic/issues/288 for possible fixes
    if source:
        body["_source"] = source

    with concurrency_limiter.run():
        search_pipeline = getattr(request.app.state, component.search_pipeline)
        search_response = search_pipeline.predict(body)
        qa_response = {}

        if (
            search_response.get("query_type", None) != "request:metadata"
            and body.get("from", 0) == 0
        ):
            qa_pipeline = getattr(request.app.state, component.qa_pipeline, None)

            if qa_pipeline and body.get("size", 0):
                query = body.pop("query")
                params = body.get("params", {})
                params.update({"custom_query": query})
                body["params"] = params
                body["query"] = get_search_term(query)

                qa_response = qa_pipeline.predict(body)

    response = remix(search_response, qa_response)
    response.pop("sentence_transformer_documents", None)

    import pdb

    pdb.set_trace()
    return response


post_querysearch.__doc__ = """ """
