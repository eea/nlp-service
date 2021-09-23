from haystack.schema import BaseComponent
from haystack.retriever import ElasticsearchRetriever
from haystack.document_store import ElasticsearchDocumentStore
from typing import List, Optional
from haystack.schema import MultiLabel, Document
import logging

logger = logging.getLogger(__name__)


class SearchlibElasticsearchDocumentStore(ElasticsearchDocumentStore):
    def query(
        self,
        query: Optional[dict],
        aggs: Optional[dict] = None,
        highlight: Optional[dict] = None,
        size: Optional[int] = None,
        track_total_hits: Optional[bool] = True,
        index: str = None
    ) -> List[Document]:
        """
        ES Docstore replacement that supports native ES queries
        """

        if index is None:
            index = self.index

        # Naive retrieval without BM25, only filtering
        body = {}
        if query:
            body['query'] = query

        if aggs:
            body['aggs'] = aggs

        if highlight:
            body['highlight'] = highlight

        if size is not None:
            body['size'] = size

        if track_total_hits is not None:
            body['track_total_hits'] = track_total_hits

        if self.excluded_meta_data:
            body["_source"] = {"excludes": self.excluded_meta_data}

        # print(json.dumps(body))
        logger.debug(f"Retriever query: {body}")

        result = self.client.search(index=index, body=body)

        return result


class RawElasticsearchRetriever(ElasticsearchRetriever):
    """ An ElasticSearch retriever variant that just passes ES queries to ES

    Note: document_store needs to be an instance of
    SearchlibElasticsearchDocumentStore
    """

    def run(self, root_node: str, aggs: Optional[dict] = None,
            highlight: Optional[dict] = None, query: Optional[dict] = None,
            size: Optional[int] = None,
            track_total_hits: Optional[bool] = True, index: str = None):

        if root_node == "Query":
            self.query_count += 1
            run_query_timed = self.timing(self.retrieve, "query_time")
            output = run_query_timed(
                query=query, aggs=aggs, highlight=highlight,
                size=size, track_total_hits=track_total_hits,
                index=index
            )
            return output, 'output_1'
        else:
            raise Exception(f"Invalid root_node '{root_node}'.")

    def retrieve(self, **kwargs):

        index = kwargs.get('index')

        if index is None:
            index = self.document_store.index

        args = kwargs.copy()
        args['index'] = index

        return self.document_store.query(**args)


class Category(BaseComponent):

    def __init__(self, *args, **kwargs):
        self.category = kwargs.get('category', 'untitled')

    def run(self):
        return {"category": self.category}, 'output_1'


class SearchQueryClassifier(BaseComponent):
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
            query: Optional[str] = None,
            file_paths: Optional[List[str]] = None,
            labels: Optional[MultiLabel] = None,
            documents: Optional[List[Document]] = None,
            meta: Optional[dict] = None,
            params: Optional[dict] = None,
            ):

        if (params or {}).get('size', 0) > 0:
            return {}, 'output_2'

        return {}, 'output_1'
