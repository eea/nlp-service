""" FastAPI data models for zeroshot classifier

See https://huggingface.co/cross-encoder/nli-roberta-base
"""

from typing import List

from pydantic import BaseModel


class ZeroShotRequest(BaseModel):
    text: str = "EU maritime transport faces a crucial decade to transition to a more economically, socially and environmentally sustainable sector. Already, most ships calling in the EU have reduced their speed by up to 20 % compared to 2008, thereby also reducing emissions, according to the report."
    candidate_labels: List[str] = ["Air pollution", "Climate change", "Biodiversity", "Land use",
                                   "Water and marine environment", "Transport", "Industry", "Energy", "Agriculture"]


class Label(BaseModel):
    label: str
    score: float


class ZeroShotResponse(BaseModel):
    labels: List[Label]

    # text: str
    # questions: List[Label]
