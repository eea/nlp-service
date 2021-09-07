""" FastAPI data models for zeroshot classifier

See https://huggingface.co/cross-encoder/nli-roberta-base
"""

from typing import List

from pydantic import BaseModel


class ZeroShotRequest(BaseModel):
    text: str
    candidate_labels: List[str]


# class Label(BaseModel):
#     question: str
#     answer: str


class ZeroShotResponse(BaseModel):
    labels: List[str]

    # text: str
    # questions: List[Label]
