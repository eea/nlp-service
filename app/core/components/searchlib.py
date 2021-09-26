from copy import deepcopy
from haystack.schema import BaseComponent
from haystack.retriever import ElasticsearchRetriever, DensePassageRetriever
from haystack.document_store import ElasticsearchDocumentStore
from typing import List, Optional, Any       # , Dict
from haystack.schema import MultiLabel, Document
import numpy as np
import logging
from elasticsearch.exceptions import RequestError
import json
from app.core.elasticsearch import get_search_term

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

    def _get_vector_similarity_query(self, body: dict, query_emb: np.ndarray):
        """
        Generate Elasticsearch query for vector similarity.
        """

        if self.similarity == "cosine":
            similarity_fn_name = "cosineSimilarity"
        elif self.similarity == "dot_product":
            similarity_fn_name = "dotProduct"
        else:
            raise Exception(
                "Invalid value for similarity in ElasticSearchDocumentStore "
                "constructor. Choose between \'cosine\' and \'dot_product\'"
            )

        query = deepcopy(body)
        if query.get('function_score', {}).get(
                'query', {}).get('bool', {}).get('must'):
            del query['function_score']['query']['bool']['must']

        script = {
            "script_score": {
                # "query": {"match_all": {}},
                "script": {
                    # offset score to ensure a positive range as required by Elasticsearch
                    "source": f"{similarity_fn_name}(params.query_vector,'{self.embedding_field}') + 1000",
                    "params": {"query_vector": query_emb.tolist()},
                },
            }
        }
        query['function_score']['functions'].append(script)
        return query

    def query_by_embedding(self,
                           query_emb: np.ndarray,
                           return_embedding: Optional[bool] = None,

                           aggs: Optional[dict] = None,
                           highlight: Optional[dict] = None,
                           index: Optional[str] = None,
                           query: Optional[dict] = None,
                           size: Optional[int] = None,
                           track_total_hits: Optional[bool] = True,
                           ) \
            -> List[Document]:
        if index is None:
            index = self.index

        if return_embedding is None:
            return_embedding = self.return_embedding

        if not self.embedding_field:
            raise RuntimeError(
                "Please specify arg `embedding_field` in "
                "ElasticsearchDocumentStore()"
            )
        else:
            # +1 in similarity to avoid negative numbers (for cosine sim)
            emb_query = self._get_vector_similarity_query(query, query_emb)
            body = {}
            if emb_query:
                body['query'] = emb_query

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

                excluded_meta_data: Optional[list] = None

            if self.excluded_meta_data:
                excluded_meta_data = deepcopy(self.excluded_meta_data)

                if return_embedding is True and \
                        self.embedding_field in excluded_meta_data:
                    excluded_meta_data.remove(self.embedding_field)
                elif return_embedding is False and \
                        self.embedding_field not in excluded_meta_data:
                    excluded_meta_data.append(self.embedding_field)
            elif return_embedding is False:
                excluded_meta_data = [self.embedding_field]

            if excluded_meta_data:
                body["_source"] = {"excludes": excluded_meta_data}

            logger.debug(f"Retriever query: {body}")
            print("query body")
            with open('/tmp/1.json', 'w') as f:
                f.write(json.dumps(body))
            print(body)
            try:
                result = self.client.search(
                    index=index,
                    body=body, request_timeout=300)["hits"]["hits"]
            except RequestError as e:
                if e.error == "search_phase_execution_exception":
                    error_message: str = (
                        "search_phase_execution_exception: Likely some of "
                        "your stored documents don't have embeddings."
                        " Run the document store's update_embeddings() "
                        "method.")
                    raise RequestError(e.status_code, error_message, e.info)
                else:
                    raise e

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


class RawDensePassageRetriever(DensePassageRetriever):
    """ A DensePassageRetriever variant that doesn't follow Haystack's query model

    Note: document_store needs to be an instance of
    SearchlibElasticsearchDocumentStore
    """

    def run(self,
            root_node: str,
            aggs: Optional[dict] = None,
            highlight: Optional[dict] = None,
            index: str = None,
            query: Optional[dict] = None,
            size: Optional[int] = None,
            track_total_hits: Optional[bool] = True,
            params: Optional[dict] = {},
            ):

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

        # Hardcoded for ES
        q = kwargs['query']
        print(q)
        # import pdb
        # pdb.set_trace()
        search_term = get_search_term(q)
        query_emb = self.embed_queries(texts=[search_term])[0]
        args['query_emb'] = query_emb

        return self.document_store.query_by_embedding(**args)


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
            query: Optional[Any] = None,
            file_paths: Optional[List[str]] = None,
            labels: Optional[MultiLabel] = None,
            documents: Optional[List[Document]] = None,
            meta: Optional[dict] = None,
            params: Optional[dict] = None,
            ):

        if (params or {}).get('size', 0) > 0:
            search_term = get_search_term(params['query'])
            if search_term:
                return {}, 'output_2'

        return {}, 'output_1'
