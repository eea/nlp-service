""" FastAPI data models for Question and Answer
"""

from typing import List

from pydantic import BaseModel


class QuestionGenerationRequest(BaseModel):
    text: str
    num_questions: int


class QA(BaseModel):
    question: str
    answer: str


class QuestionGenerationResponse(BaseModel):
    text: str
    questions: List[QA]
