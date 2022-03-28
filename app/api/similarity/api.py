""" FastAPI data models for similarity computation model
"""

from typing import Any, List

from pydantic import BaseModel


class SimilarityRequest(BaseModel):
    base: str = "eight accidental medium to large oil tanker spills out of a worldwide total of 62 occurred in EU waters over the past decade"
    candidates: List[str] = [
        "underwater noise levels in EU waters have more than doubled between 2014 and 2019",
        "maritime transport can keep growing and delivering on our citizens’ daily needs, in harmony with the environment",
        "out of a total of 18 large accidental oil spills in the word since 2010, only three were located in the EU (17%)",
    ]


class Prediction(BaseModel):
    text: str
    score: float


class SimilarityResponse(BaseModel):
    base: str
    predictions: List[Prediction]
    clusters: List[Any]
