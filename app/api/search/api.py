""" FastAPI data models for semantic search in a data store
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class SearchRequest(BaseModel):
    """A search request

    See also https://github.com/samuelcolvin/pydantic/issues/153
    """

    class Config:
        allow_population_by_field_name = True
        fields = {"from_": "from"}

    runtime_mappings: Optional[Dict]
    from_: Optional[int] = 0
    query: Optional[Dict]
    aggs: Optional[Dict]
    highlight: Optional[Dict]
    size: Optional[int] = 10
    sort: Optional[List]
    track_total_hits: Optional[bool] = True
    explain: Optional[bool] = False
    params: Optional[Dict] = None
    source: Optional[Dict] = None
    suggest: Optional[Dict] = None
    index: Optional[str] = None


class Document(BaseModel):
    text: str
    id: str
    score: Optional[float] = None
    meta: Optional[Dict[str, Any]]


class SearchResponse(BaseModel):
    """A search response"""

    hits: Optional[List[Any]]
    aggregations: Optional[dict]
    query_type: Optional[str]

    # documents: List
