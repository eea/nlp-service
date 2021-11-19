""" FastAPI data models for tika conversion
"""

from pydantic import BaseModel
from typing import Any, Dict, List, Optional


class TikaRequest(BaseModel):
    url: str = "https://www.eea.europa.eu/api/SITE/publications/" \
        "exploring-the-social-challenges-of/at_download/file"


class Document(BaseModel):
    text: str
    id: str = None
    score: Optional[float] = None
    meta: Optional[Dict[str, Any]]


class TikaResponse(BaseModel):
    documents: List[Document]
