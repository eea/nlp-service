""" FastAPI data models for similarity computation model
"""

from typing import List

from pydantic import BaseModel


class EmbeddingRequest(BaseModel):
    is_passage: bool = False
    snippets: List[str] = [
        "Where Is The Best APPLE JUST ANNOUNCED A NEW IPHONE?",
        "27 Ways To Improve your stance",
        "Avoid The Top 10 Mistakes Made By Beginning photographer"
    ]


class Embedding(BaseModel):
    text: str
    embedding: List[float]


class EmbeddingResponse(BaseModel):
    embeddings: List[Embedding]
