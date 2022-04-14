from typing import Dict, List, Literal, Optional, Union

from haystack.schema import Answer, Document, Label
from pydantic import BaseModel, Extra


class FeedbackResponse(BaseModel):
    """ """

    # status: str = Literal["ok"]


class AnswerSerialized(Answer):
    context: Optional[str] = None


class DocumentSerialized(Document):
    content: str
    embedding: Optional[List[float]]  # type: ignore


class LabelSerialized(Label, BaseModel):
    document: DocumentSerialized
    answer: Optional[AnswerSerialized] = None


class CreateLabelSerialized(BaseModel):
    id: Optional[str] = None
    query: str
    document: DocumentSerialized
    is_correct_answer: bool
    is_correct_document: bool
    origin: Literal["user-feedback", "gold-label"]
    answer: Optional[AnswerSerialized] = None
    no_answer: Optional[bool] = None
    pipeline_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    meta: Optional[dict] = None
    filters: Optional[dict] = None

    class Config:
        # Forbid any extra fields in the request to avoid silent failures
        extra = Extra.forbid


class FilterRequest(BaseModel):
    filters: Optional[Dict[str, Optional[Union[str, List[str]]]]] = None


class FeedbackRequest(BaseModel):
    answer: str
    question: str
    context: str
    document_id: str
    score: Optional[float]
    is_correct_answer: bool
    is_correct_document: bool
    no_answer: Optional[bool] = None
    offsets_in_context: Optional[list]
    offsets_in_document: Optional[list]
    origin: str = "user-feedback"
    meta: Optional[dict]

    # document: DocumentSerialized
