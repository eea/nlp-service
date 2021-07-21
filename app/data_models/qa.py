from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel


class QA_Request(BaseModel):
    query: str
    custom_query: str
    # filters: Optional[Dict[str, Optional[Union[str, List[str]]]]] = None
    top_k_retriever: Optional[int] = None
    top_k_reader: Optional[int] = None


class Answer(BaseModel):

    answer: Optional[str]
    question: Optional[str]
    score: Optional[float] = None
    probability: Optional[float] = None
    context: Optional[str]
    offset_start: int
    offset_end: int
    offset_start_in_doc: Optional[int]
    offset_end_in_doc: Optional[int]
    document_id: Optional[str] = None
    id: Optional[str] = None
    source: Optional[Dict[str, Any]]
    # meta: Optional[Dict[str, Any]]


class Response(BaseModel):
    query: str
    answers: List[Answer]
