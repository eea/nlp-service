""" Routes for the QA Search service
"""
import copy
import logging
from datetime import datetime

from app.api.search.api import SearchRequest
from app.core.config import CONCURRENT_REQUEST_PER_WORKER
from app.core.elasticsearch import get_body_from  # , get_search_term

# from app.core.elasticsearch import get_search_term
from app.core.utils import RequestLimiter
from fastapi import APIRouter, Request

# from .api import QASearchResponse

router = APIRouter()

logger = logging.getLogger(__name__)

concurrency_limiter = RequestLimiter(CONCURRENT_REQUEST_PER_WORKER)


def remix(search_response, qa_response, exclude=None):
    """Cleanup/mix the Search response with the QA response"""

    exclude_fields = exclude or []
    res = {}
    res.update(search_response)
    res.update(qa_response)

    fields = ["elasticsearch_result", "documents", "params", "highlight", "elapsed"]

    for field in fields:
        res.pop(field, None)

    hits = res.get("hits", {}).get("hits", [])
    for hit in hits:
        for field in exclude_fields:
            if field in hit.get("_source", {}):
                del hit["_source"][field]

    res["elapsed"] = {
        "search": search_response.get("elapsed", []),
        "qa": qa_response.get("elapsed", []),
    }
    return res


_missing = object()


def is_qa_request(body, response, default_query_types):
    """Current request should provide answers, or is a metadata req?"""

    from_ = get_body_from(body)
    query_type = response.get("query_type", None)

    params = body.get("params", {}) or {}
    handled_types = params.get("QuerySearch", {}).get("query_types", _missing)

    if handled_types is _missing:
        handled_types = default_query_types

    return (query_type in handled_types) and (from_ == 0)  # "request:metadata"


def remove_attribute(tree, attribute):
    if isinstance(tree, dict):
        if tree.get(attribute, None) is not None:
            del tree[attribute]
        for node in tree.keys():
            remove_attribute(tree[node], attribute)
    if isinstance(tree, list):
        for node in tree:
            remove_attribute(node, attribute)


def remove_nodes_with_attribute(tree, attribute):
    if isinstance(tree, dict):
        for node in list(tree.keys()):
            if (
                isinstance(tree[node], dict)
                and tree[node].get(attribute, None) is not None
            ):
                del tree[node]
                continue
            remove_nodes_with_attribute(tree[node], attribute)
    if isinstance(tree, list):
        for node in tree:
            if isinstance(node, dict) and node.get(attribute, None) is not None:
                del node
                continue
            remove_nodes_with_attribute(node, attribute)


def remove_empty_nodes(tree):
    if isinstance(tree, dict):
        for node in list(tree.keys()):
            remove_empty_nodes(tree[node])
            if isinstance(tree[node], dict) and len(tree[node].keys()) == 0:
                del tree[node]
            else:
                if isinstance(tree[node], list) and len(tree[node]) == 0:
                    del tree[node]

    if isinstance(tree, list):
        for node in tree:
            remove_empty_nodes(node)
            try:
                tree.remove({})
            except:
                pass
            try:
                tree.remove([])
            except:
                pass


@router.post("")  # , response_model=QASearchResponse
def post_querysearch(payload: SearchRequest, request: Request):
    q_id = datetime.timestamp(datetime.now())
    try:
        component = request.app.state.querysearch.component
        excluded_meta_data = component.excluded_meta_data
        default_query_types = component.default_query_types

        body = payload.dict()
        # use_dp = body.get("params", {}).pop("use_dp", False)
        body.update(body.get("params", {}) or {})
        source = body.pop("source", None)

        print(f'{q_id} {body}')
        # pydantic doesn't like fields with _underscore in beginning?
        # See https://github.com/samuelcolvin/pydantic/issues/288
        # for possible fixes

        body["q_id"] = q_id

        if source:
            body["_source"] = source
        search_body = copy.deepcopy(body)
        remove_attribute(search_body, "ignoreFromNlp")
        qa_body = copy.deepcopy(body)
        remove_nodes_with_attribute(qa_body, "ignoreFromNlp")
        remove_empty_nodes(qa_body)

        with concurrency_limiter.run():
            search_pipeline = getattr(request.app.state, component.search_pipeline)
            search_response = search_pipeline.predict(search_body)
            qa_response = {}

            if is_qa_request(qa_body, search_response, default_query_types):
                qa_pipeline = getattr(request.app.state, component.qa_pipeline, None)

                if qa_pipeline and qa_body.get("size", 0):
                    # query = body.pop("query")
                    # params = body.get("params", {})
                    # params.update({"custom_query": query})
                    # body["params"] = params
                    # body["query"] = get_search_term(query)
                    qa_body["params"]["scope_answerextraction"] = True
                    qa_response = qa_pipeline.predict(qa_body)

        response = remix(search_response, qa_response, excluded_meta_data)
        response.pop("sentence_transformer_documents", None)

        answers = response.get("answers", [])
        if answers:
            for hit in answers:
                for field in excluded_meta_data:
                    if field in hit:
                        del hit[field]
                    if field in hit.get("source", []):
                        del hit["source"][field]

        hits = response.get("hits", {}).get("hits", [])
        for hit in hits:
            for field in excluded_meta_data:
                if field in hit:
                    del hit[field]
                if field in hit.get("source", []):
                    del hit["source"][field]

        return response
    except Exception as e:
        logger.exception(f"{q_id} {str(e)}")
        return {"errors":[f"{q_id} {str(e)}"]}

post_querysearch.__doc__ = """ """
