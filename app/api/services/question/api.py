""" FastAPI data models for Question/Statement classifier
"""

from typing import Literal

from pydantic import BaseModel


class QuestionRequest(BaseModel):
    query: str


class QuestionResponse(BaseModel):
    answer: Literal['question', 'statement']
