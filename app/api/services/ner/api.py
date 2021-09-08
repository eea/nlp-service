""" FastAPI data models for zeroshot classifier

See https://huggingface.co/cross-encoder/nli-roberta-base
"""

from typing import List

from pydantic import BaseModel


class NERRequest(BaseModel):
    text: str = "Apple just announced the newest iPhone X"


class NERResponse(BaseModel):
    entities: List[dict]
