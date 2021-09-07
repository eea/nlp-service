""" FastAPI data models for zeroshot classifier

See https://huggingface.co/cross-encoder/nli-roberta-base
"""

from typing import List

from pydantic import BaseModel


class ZeroShotRequest(BaseModel):
    text: str = "Apple just announced the newest iPhone X"
    candidate_labels: List[str] = ["technology", "sports", "politics"]


class Label(BaseModel):
    label: str
    score: float


class ZeroShotResponse(BaseModel):
    labels: List[Label]

    # text: str
    # questions: List[Label]
