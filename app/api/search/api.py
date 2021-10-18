""" FastAPI data models for semantic search in a data store
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


# class SearchRequestParams(BaseModel):
#     custom_query: Optional[Dict]
#     top_k: Optional[int] = 10
#
#     # filters: Optional[Dict[str, Optional[Union[str, List[str]]]]] = {}


class SearchRequest(BaseModel):
    """ A search request

    See also https://github.com/samuelcolvin/pydantic/issues/153
    """

    class Config:
        allow_population_by_field_name = True
        fields = {
            'from_': 'from'
        }

    runtime_mappings: Optional[Dict]
    from_: Optional[int] = 0
    query: Optional[Dict]
    aggs: Optional[Dict]
    highlight: Optional[Dict]
    size: Optional[int] = 10
    sort: Optional[List]
    track_total_hits: Optional[bool] = True


class Document(BaseModel):
    text: str
    id: str
    score: Optional[float] = None
    meta: Optional[Dict[str, Any]]


class SearchResponse(BaseModel):
    """ A search response
    """
    # documents: List
