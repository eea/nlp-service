""" FastAPI data models for Question and Answer
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class QA_RequestParams(BaseModel):
    use_dp: bool = True
    custom_query: Optional[dict]
    RawRetriever: Optional[dict]
    DensePassageRetriever: Optional[dict]
    AnswerExtraction: Optional[dict]

    # top_k_retriever: Optional[int] = 10
    # top_k_reader: Optional[int] = 10
    # filters: Optional[Dict[str, Optional[Union[str, List[str]]]]] = None


class QA_Request(BaseModel):
    query: str = "What is GHG"
    params: Optional[QA_RequestParams] = None


class Answer(BaseModel):

    answer: Optional[str]
    text: Optional[str]
    body: Optional[str]
    question: Optional[str]
    score: Optional[float] = None
    probability: Optional[float] = None
    context: Optional[str]
    full_context: Optional[str]
    offset_start: int
    offset_end: int
    offset_start_in_doc: Optional[int]
    offset_end_in_doc: Optional[int]
    document_id: Optional[str] = None
    id: Optional[str] = None
    source: Optional[Dict[str, Any]]
    meta: Optional[Dict[str, Any]]

    original_answer: Optional[dict] = None


class QA_Response(BaseModel):
    query: Optional[str]
    answers: Optional[List[Answer]]
    # documents: List[Answer]
