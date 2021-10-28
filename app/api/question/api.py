""" FastAPI data models for Question/Statement classifier
"""

from pydantic import BaseModel


class QuestionRequest(BaseModel):
    query: str = "Where to go on holiday"


class QuestionResponse(BaseModel):
    answer: str
