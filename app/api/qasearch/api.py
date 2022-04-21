from typing import Optional, Union

from app.api.qa.api import QA_Response
from app.api.search.api import SearchResponse

QASearchResponse = Union[Optional[SearchResponse], Optional[QA_Response]]
