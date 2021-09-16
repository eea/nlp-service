""" FastAPI data models for zeroshot classifier

See https://huggingface.co/cross-encoder/nli-roberta-base
"""

import os
from typing import List

from pydantic import BaseModel

sample_name = os.path.join(os.path.dirname(__file__), 'sample.txt')
with open(sample_name) as f:
    sample_text = f.read().strip()


class NERRequest(BaseModel):
    texts: List[str] = [sample_text]


class NERResponse(BaseModel):
    entities: List[dict]
