""" FastAPI data models for similarity computation model
"""

from typing import List

from pydantic import BaseModel


class SimilarityRequest(BaseModel):
    base: str = "Apple just announced the newest iPhone X"
    candidates: List[str] = [
        "Where Is The Best APPLE JUST ANNOUNCED A NEW IPHONE?",
        "27 Ways To Improve your stance",
        "Avoid The Top 10 Mistakes Made By Beginning photographer"
    ]


class Prediction(BaseModel):
    text: str
    score: float


class SimilarityResponse(BaseModel):
    base: str
    predictions: List[Prediction]
