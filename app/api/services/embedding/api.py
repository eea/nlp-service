""" FastAPI data models for similarity computation model
"""

from typing import List

from pydantic import BaseModel


class EmbeddingRequest(BaseModel):
    is_passage: bool = False
    snippets: List[str] = [
        "Maritime transport plays and will continue to play an essential role in global and European trade and economy.",
        "The European Environment Agency provides sound, independent information on the environment for those involved in developing, adopting, implementing and evaluating environmental policy, and also the general public.",
        "Climate-friendly practices for sourcing raw materials hold significant potential to cut greenhouse gas emissions in Europe and globally."
    ]


class Embedding(BaseModel):
    text: str
    embedding: List[float]


class EmbeddingResponse(BaseModel):
    embeddings: List[Embedding]
