""" FastAPI data models for spacy-based Named Entity Recognition
"""
import os

from typing import Any, List

from pydantic import BaseModel

with open(os.path.join(os.path.dirname(__file__), 'data.txt')) as f:
    text = f.read().strip()


class SpacyNERRequest(BaseModel):
    texts: List[str] = [text]


class SpacyNERResponse(BaseModel):
    documents: List[Any]
