import logging
from typing import Any, List, Optional  # , Dict

from app.core.elasticsearch import get_search_term  # get_body_from,
from haystack.nodes.base import BaseComponent
from haystack.schema import Document, MultiLabel

logger = logging.getLogger(__name__)


class Category(BaseComponent):
    outgoing_edges = 1

    def __init__(self, category, *args, **kwargs):
        self.category = category or "untitled"

    def run(self):
        return {"query_type": self.category}, "output_1"

    def run_batch(self, *args, **kwargs):
        # TODO: implement this
        raise ValueError
        return {}, "output_1"


class DPRequestClassifier(BaseComponent):
    outgoing_edges = 2

    def run(self, params=None, payload=None):
        params = params or {}
        params = params.get("payload", {}).get("params", {}) or {}
        use_dp = params.get(self.name, {}).get("use_dp", False)

        print("----------------------------")
        print("----------------------------")
        print("----------------------------")
        print("DPRC")
        if use_dp:
            print("output_2")
        else:
            print("output_1")
        return {}, use_dp and "output_2" or "output_1"

    def run_batch(self, *args, **kwargs):
        # TODO: implement this
        raise ValueError
        return {}, "output_1"


class ElasticSearchRequestClassifier(BaseComponent):
    """A classifier and search query adapter for incoming requests from ES

    - output_1: Aggregation queries, they go to "raw index"
    - output_2: Haystack-native, send a haystack-compatible query in pipeline
    """

    outgoing_edges = 2

    def run(
        self,
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

        payload = params["payload"] or {}
        q_id = payload.get("q_id")
        print(f"{q_id} ERC {payload}")

        #        import pdb; pdb.set_trace()
        if payload.get("size", 0) > 0:
            search_term = get_search_term(payload["query"])
            print(f"{q_id} searchterm {search_term}")
            if search_term:
                print(f"{q_id} output_2")
                return {"query": search_term}, "output_2"

        print(f"{q_id} output_1")
        return {}, "output_1"

    def run_batch(self, *args, **kwargs):
        # TODO: implement this
        raise ValueError
        return {}, "output_1"
