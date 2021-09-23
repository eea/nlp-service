""" FastAPI data models for semantic search in a data store
"""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel


class SearchRequestParams(BaseModel):
    filters: Optional[Dict[str, Optional[Union[str, List[str]]]]] = {}
    top_k: Optional[int] = 10


class SearchRequest(BaseModel):
    """ A search request
    """
    query: Optional[str] = 'water quality'
    params: Optional[SearchRequestParams] = None


class Document(BaseModel):
    text: str
    id: str
    score: Optional[float] = None
    meta: Optional[Dict[str, Any]]


class SearchResponse(BaseModel):
    """ A search response
    """
    documents: List
