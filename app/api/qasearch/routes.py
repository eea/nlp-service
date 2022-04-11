import logging
from typing import Dict, Optional, Union

from app.api.search.api import SearchRequest
from fastapi import APIRouter, Request
from haystack.schema import Answer, Document, Label

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("")
def post_querysearch(payload: SearchRequest, request: Request):
    component = request.app.state.querysearch.component

    import pdb

    pdb.set_trace()
    # search_pipeline = component.search_pipeline
    # qa_pipeline = component.qa_pipeline

    return {"status": "ok"}


post_querysearch.__doc__ = """

"""
