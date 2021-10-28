from haystack.schema import BaseComponent
from typing import List, Optional, Any       # , Dict
from haystack.schema import MultiLabel, Document
import logging
from app.core.elasticsearch import get_search_term

logger = logging.getLogger(__name__)


class Category(BaseComponent):
    outgoing_edges = 1

    def __init__(self, *args, **kwargs):
        self.category = kwargs.get('category', 'untitled')

    def run(self):
        return {"query_type": self.category}, 'output_1'


class ElasticSearchRequestClassifier(BaseComponent):
    """ A classifier and search query adapter for incoming requests from ES

    - output_1: Aggregation queries, they go to "raw index"
    - output_2: Haystack-native, send a haystack-compatible query in pipeline
    """
    outgoing_edges = 2

    def run(self,
            # aggs,
            # highlight,
            # query,
            # size,
            # track_total_hits
            query: Optional[Any] = None,
            file_paths: Optional[List[str]] = None,
            labels: Optional[MultiLabel] = None,
            documents: Optional[List[Document]] = None,
            meta: Optional[dict] = None,
            params: Optional[dict] = None,
            ):

        payload = params['payload']
        if (payload or {}).get('size', 0) > 0:
            search_term = get_search_term(payload['query'])
            if search_term:
                return {"query": search_term}, 'output_2'

        return {}, 'output_1'
