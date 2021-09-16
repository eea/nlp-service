""" FastAPI data models for preprocessing
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class PreprocessRequest(BaseModel):
    documents: List
    cleanup_pipeline: str = 'cleanup'


class Document(BaseModel):
    id: Optional[str] = None
    context: Optional[str]
    source: Optional[Dict[str, Any]]


class Response(BaseModel):
    documents: List
