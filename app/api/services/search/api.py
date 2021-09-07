""" FastAPI data models for simple search in a data store
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str
    # filters: Optional[Dict[str, Optional[Union[str, List[str]]]]] = None
    top_k_retriever: Optional[int] = None


class Document(BaseModel):
    score: Optional[float] = None
    probability: Optional[float] = None
    context: Optional[str]
    document_id: Optional[str] = None
    meta: Optional[Dict[str, Any]]


class SearchResponse(BaseModel):
    query: str
    documents: List[Document]
