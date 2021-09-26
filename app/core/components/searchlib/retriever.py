import logging

from haystack.retriever import ElasticsearchRetriever, DensePassageRetriever
from typing import Optional
from app.core.elasticsearch import get_search_term

logger = logging.getLogger(__name__)


class RawElasticsearchRetriever(ElasticsearchRetriever):
    """ An ElasticSearch retriever variant that just passes ES queries to ES

    Note: document_store needs to be an instance of
    SearchlibElasticsearchDocumentStore
    """

    def run(self, root_node: str, params: dict, index: str = None):
        # aggs: Optional[dict] = None,
        # highlight: Optional[dict] = None, query: Optional[dict] = None,
        # size: Optional[int] = None,
        # track_total_hits: Optional[bool] = True,
        body = params['payload']

        if root_node == "Query":
            self.query_count += 1
            run_query_timed = self.timing(self.retrieve, "query_time")
            output = run_query_timed(
                index=index, **body
            )
            if isinstance(output, list):
                output = {'result': output}
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


class RawDensePassageRetriever(DensePassageRetriever):
    """ A DensePassageRetriever variant that doesn't follow Haystack's query model

    Note: document_store needs to be an instance of
    SearchlibElasticsearchDocumentStore
    """

    def run(self,
            root_node: str,
            # aggs: Optional[dict] = None,
            # highlight: Optional[dict] = None,
            # query: Optional[dict] = None,
            # size: Optional[int] = None,
            # track_total_hits: Optional[bool] = True,
            params: Optional[dict] = {},
            index: str = None,
            ):

        body = params['payload']

        if root_node == "Query":
            self.query_count += 1
            run_query_timed = self.timing(self.retrieve, "query_time")
            output = run_query_timed(
                index=index,
                **body,
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

        # Hardcoded for ES
        q = kwargs['query']
        print(q)
        search_term = get_search_term(q)
        query_emb = self.embed_queries(texts=[search_term])[0]
        args['query_emb'] = query_emb

        return self.document_store.query_by_embedding(**args)
