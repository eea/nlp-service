""" FastAPI data models for sentence embeddings model
"""

from typing import List

from pydantic import BaseModel


class SplitRequest(BaseModel):
    fulltext: str = "Maritime transport plays and will continue to play an essential role in global and European trade and economy."
    clean_empty_lines: bool = True
    clean_whitespace: bool = True
    clean_header_footer: bool = False
    split_by: str = "word"
    split_length: int = 10
    split_respect_sentence_boundary: bool = True
    split_overlap: int = 0

class SplitResponse(BaseModel):
    parts: List[str]
