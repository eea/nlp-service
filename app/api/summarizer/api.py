""" FastAPI data models for Summarizers
"""

import os
from typing import Any, List

from pydantic import BaseModel

sample_name = os.path.join(os.path.dirname(__file__), 'sample.txt')
with open(sample_name) as f:
    sample_text = f.read().strip()


class SummaryRequest(BaseModel):
    documents: List[str] = [sample_text]
    # max_length: int = 250
    # min_length: int = 5


class SummaryResponse(BaseModel):
    documents: List[Any]
