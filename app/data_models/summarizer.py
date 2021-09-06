""" FastAPI data models for Summarizers
"""

from typing import Literal

from pydantic import BaseModel


class SummaryRequest(BaseModel):
    query: str


class SummaryResponse(BaseModel):
    answer: str
