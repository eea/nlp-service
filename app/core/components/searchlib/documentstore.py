import logging
import re
from copy import deepcopy
from datetime import datetime
from typing import Any, List, Optional, Union  # , Dict

import numpy as np
from app.core.config import NLP_FIELD
from app.core.elasticsearch import get_search_term
from elasticsearch.exceptions import RequestError
from haystack.document_stores.elasticsearch import ElasticsearchDocumentStore
from haystack.nodes.base import BaseComponent
from haystack.schema import Document, MultiLabel

logger = logging.getLogger(__name__)


class SearchlibElasticsearchDocumentStore(ElasticsearchDocumentStore):
    def __init__(
        self,
        host: Union[str, List[str]] = "localhost",
        port: Union[int, List[int]] = 9200,
        username: str = "",
        password: str = "",
        api_key_id: Optional[str] = None,
        api_key: Optional[str] = None,
        aws4auth=None,
        index: str = "document",
        label_index: str = "label",
        search_fields: Union[str, list] = "content",
        content_field: str = "content",
        name_field: str = "name",
        embedding_field: str = "embedding",
        embedding_dim: int = 768,
        custom_mapping: Optional[dict] = None,
        excluded_meta_data: Optional[list] = None,
        analyzer: str = "standard",
        scheme: str = "http",
        ca_certs: Optional[str] = None,
        verify_certs: bool = True,
        recreate_index: bool = False,
        create_index: bool = True,
        refresh_type: str = "wait_for",
        similarity="dot_product",
        timeout=30,
        return_embedding: bool = False,
        duplicate_documents: str = "overwrite",
        index_type: str = "flat",
        scroll: str = "1d",
        skip_missing_embeddings: bool = True,
        synonyms: Optional[List] = None,
        synonym_type: str = "synonym",
        internal_excluded_meta_data: Optional[list] = None,
        nested_content_field: str = "content",
    ):
        super(SearchlibElasticsearchDocumentStore, self).__init__(
            host=host,
            port=port,
            username=username,
            password=password,
            api_key_id=api_key_id,
            api_key=api_key,
            aws4auth=aws4auth,
            index=index,
            label_index=label_index,
            search_fields=search_fields,
            content_field=content_field,
            name_field=name_field,
            embedding_field=embedding_field,
            embedding_dim=embedding_dim,
            custom_mapping=custom_mapping,
            excluded_meta_data=excluded_meta_data,
            analyzer=analyzer,
            scheme=scheme,
            ca_certs=ca_certs,
            verify_certs=verify_certs,
            recreate_index=recreate_index,
            create_index=create_index,
            refresh_type=refresh_type,
            similarity=similarity,
            timeout=timeout,
            return_embedding=return_embedding,
            duplicate_documents=duplicate_documents,
            index_type=index_type,
            scroll=scroll,
            skip_missing_embeddings=skip_missing_embeddings,
            synonyms=synonyms,
            synonym_type=synonym_type,
        )

        self.internal_excluded_meta_data = internal_excluded_meta_data
        self.nested_content_field = nested_content_field

    def query(
        self,
        query: Optional[dict],
        custom_query: Optional[dict] = None,
        runtime_mappings: Optional[dict] = None,
        aggs: Optional[dict] = None,
        highlight: Optional[dict] = None,
        size: Optional[int] = None,
        from_: Optional[int] = 0,
        sort: Optional[Any] = None,
        track_total_hits: Optional[bool] = True,
        explain: Optional[bool] = False,
        _source: Optional[dict] = None,
        index: str = None,
        suggest: Optional[dict] = None,
    ) -> List[Document]:
        """
        ES Docstore replacement that supports native ES queries
        """

        # TODO: use custom_query

        if index is None:
            index = self.index

        # Naive retrieval without BM25, only filtering
        body = {}
        if query:
            body["query"] = query

        if runtime_mappings:
            body["runtime_mappings"] = runtime_mappings

        if custom_query:
            body["query"] = custom_query

        if aggs:
            body["aggs"] = aggs

        if highlight:
            body["highlight"] = highlight

        if size is not None:
            body["size"] = size

        if from_ is not None:
            body["from"] = from_

        if track_total_hits is not None:
            body["track_total_hits"] = track_total_hits

        if explain is not None:
            body["explain"] = explain

        if _source:
            body["_source"] = _source

        if suggest is not None:
            body["suggest"] = suggest

        if self.excluded_meta_data:
            if not body["_source"].get("excludes"):
                body["_source"]["_excludes"] = []
            body["_source"]["excludes"] = (
                self.excluded_meta_data + body["_source"]["_excludes"]
            )

        if self.internal_excluded_meta_data:
            excludes_list = body.get("_source", {}).get("excludes", [])
            if len(excludes_list) == 0:
                body["_source"] = {"excludes": self.internal_excluded_meta_data}

            excludes_list = body.get("_source", {}).get("excludes", [])
            logger.info(f"exclude fields: {excludes_list}")

        if sort is not None:
            body["sort"] = sort

        logger.info(f"Retriever query: {index} {body}")
        before = datetime.now()
        result = self.client.search(index=index, body=body)
        after = datetime.now()
        delta = after - before
        logger.info(f"RESULTS in {delta.total_seconds()} seconds")
        return result

    def _get_vector_similarity_query(
        self, body: dict, query_emb: np.ndarray, custom_query: Optional[dict] = None
    ):
        """
        Generate Elasticsearch query for vector similarity.

        The original query looks like:

        query = {
            'function_score': {
                'functions': [],
                'query': {
                    'bool': {
                        'filter': [
                            {'bool': {'minimum_should_match': 1, 'should': [ {'term': {'language': 'en'}}]}},
                            {'bool': {'minimum_should_match': 1, 'should': [ {'range': {'readingTime': {}}}]}},
                            {'term': {'hasWorkflowState': 'published'}},
                            {'constant_score': {'filter': {'bool': {'should': [{'bool': {'must_not': {'exists': { 'field': 'expires'}}}}, {'range': {'expires': {'gte': '2021-09-29T12:16:09Z'}}}]}}}}
                        ],
                        # 'must': [
                        #     {'multi_match':
                        #      {'fields': ['title^2',
                        #                  'subject^1.5',
                        #                  'description^1.5',
                        #                  'searchable_spatial^1.2',
                        #                  'searchable_places^1.2',
                        #                  'searchable_objectProvides^1.4',
                        #                  'searchable_topics^1.2',
                        #                  'searchable_time_coverage^10',
                        #                  'searchable_organisation^2',
                        #                  'label',
                        #                  'all_fields_for_freetext'],
                        #       'query': 'what '
                        #       'is '
                        #       'the '
                        #       'best '
                        #       'country '
                        #       'at '
                        #       'reducing '
                        #       'polution?'
                        #       }}]
                      }
                  },
            'score_mode': 'sum'
            }
        }


        We want to get to a state where the query looks like:

        {
          "size":4,
          "_source":{
            "excludes":[
              "embedding"
            ]
          },
          "query": {
            "function_score":{
              "query":{
                "script_score":{
                  "query":{
                    "bool":{
                      "filter":[
                        { "bool":{ "should":[ { "term":{ "language":"en" } } ], "minimum_should_match":1 } },
                        { "bool":{ "should":[ { "range":{ "readingTime":{ } } } ], "minimum_should_match":1 } },
                        { "term":{ "hasWorkflowState":"published" } },
                        { "constant_score":{ "filter":{ "bool":{ "should":[ { "bool":{ "must_not":{ "exists":{ "field":"expires" } } } }, { "range":{ "expires":{ "gte":"2021-09-28T10:15:55Z" } } } ] } } } }
                      ]
                    }
                  },
                  "script":{
                    "source":"dotProduct(params.query_vector,'embedding') + 1000",
                    "params":{
                      "query_vector":[
                      ]
                    }
                  }
                }
              }
            }
          }
        }
        """
        full_path = f"{NLP_FIELD}.{self.embedding_field}"

        if self.similarity == "cosine":
            # The script adds 1.0 to the cosine similarity to prevent the score from being negative.
            script_source = f"""
                (cosineSimilarity(params.query_vector, '{full_path}') + 1.0)
            """
        elif self.similarity == "dot_product":
            # Using the standard sigmoid function prevents scores from being negative.
            script_source = f"""
              double value = dotProduct(params.query_vector, '{full_path}');
              return sigmoid(1, Math.E, -value);
            """
        else:
            raise Exception(
                "Invalid value for similarity in ElasticSearchDocumentStore "
                "constructor. Choose between 'cosine' and 'dot_product'"
            )

        semantic_score = {
            "nested": {
                "inner_hits": {},
                "path": NLP_FIELD,
                "score_mode": "max",
                "query": {
                    "function_score": {
                        "script_score": {
                            "script": {
                                "source": script_source,
                                "params": {
                                    "query_vector": query_emb.tolist(),
                                },
                            }
                        }
                    }
                },
            }
        }

        query = deepcopy(custom_query or body)
        try:
            query_must = query["function_score"]["query"]["bool"]["must"]
        except KeyError:
            query_must = []
        try:
            query_filters = query["function_score"]["query"]["bool"]["filter"]
        except KeyError:
            query_filters = []
        try:
            query_functions = query["function_score"]["functions"]
        except KeyError:
            query_functions = []

        # TODO: Check if combining exact matches scores with semantic score
        # TODO: improve the quality of the results.
        query = {
            "function_score": {
                "query": {
                    "bool": {
                        "must": [semantic_score],
                        "filter": query_filters,
                    }
                },
                "functions": query_functions,
                "score_mode": "sum",
            }
        }
        # print('---[ ES Embedding query ]------')
        # print(query)
        # print('---------')
        return query

    def query_by_embedding(
        self,
        query_emb: np.ndarray,
        return_embedding: Optional[bool] = None,
        custom_query: Optional[dict] = None,
        runtime_mappings: Optional[dict] = None,
        aggs: Optional[dict] = None,
        highlight: Optional[dict] = None,
        index: Optional[str] = None,
        query: Optional[dict] = None,
        from_: Optional[int] = 0,
        size: Optional[int] = 5,
        sort: Optional[Any] = None,
        track_total_hits: Optional[bool] = True,
        explain: Optional[bool] = False,
        _source: Optional[dict] = None,
        suggest: Optional[dict] = None,
    ) -> List[Document]:
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
            emb_query = self._get_vector_similarity_query(
                body=query, query_emb=query_emb, custom_query=custom_query
            )
            body = {}

            if from_ is not None:
                body["from"] = from_

            if runtime_mappings:
                body["runtime_mappings"] = runtime_mappings

            if emb_query:
                body["query"] = emb_query

            if aggs:
                body["aggs"] = aggs

            if highlight:
                body["highlight"] = highlight

            if size is not None:
                body["size"] = size

            if track_total_hits is not None:
                body["track_total_hits"] = track_total_hits

            if explain is not None:
                body["explain"] = explain

            if _source:
                body["_source"] = _source

            if suggest is not None:
                body["suggest"] = suggest

            if self.excluded_meta_data:
                body["_source"] = {"excludes": self.excluded_meta_data}

                excluded_meta_data: Optional[list] = None

            if self.excluded_meta_data:
                excluded_meta_data = deepcopy(self.excluded_meta_data)

                if (
                    return_embedding is True
                    and self.embedding_field in excluded_meta_data
                ):
                    excluded_meta_data.remove(self.embedding_field)
                elif (
                    return_embedding is False
                    and self.embedding_field not in excluded_meta_data
                ):
                    excluded_meta_data.append(self.embedding_field)
            elif return_embedding is False:
                excluded_meta_data = [self.embedding_field]

            if excluded_meta_data:
                body["_source"] = {"excludes": excluded_meta_data}

            if self.internal_excluded_meta_data:
                excludes_list = body.get("_source", {}).get("excludes", [])
                excludes_list += self.internal_excluded_meta_data
                body["_source"] = {"excludes": excludes_list}

                excludes_list = body.get("_source", {}).get("excludes", [])
                logger.info(f"exclude fields: {excludes_list}")

            logger.info(f"DeepRetriever query: {index} - {body}")
            # print("query body")
            # with open('/tmp/1.json', 'w') as f:
            #     f.write(json.dumps(body))
            # print(body)
            try:
                result = self.client.search(index=index, body=body, request_timeout=300)
            except RequestError as e:
                if e.error == "search_phase_execution_exception":
                    error_message: str = (
                        "search_phase_execution_exception: Likely some of "
                        "your stored documents don't have embeddings."
                        " Run the document store's update_embeddings() "
                        "method."
                    )
                    raise RequestError(e.status_code, error_message, e.info)
                else:
                    raise e

            return result


def clean_text(text, conf):
    """
    replace all the expressions from document with the expressions replacement
    """
    for row in conf:
        if row["expression"]:
            text = re.sub(row["expression"], row["replacement"], text)

    return text


class ESHit2HaystackDoc(BaseComponent):
    """A component that converts raw elasticsearch hits to Haystack Documents"""

    outgoing_edges = 1

    def __init__(
        self, document_store=None, nested_vector_field="nlp_250", clean_config=None
    ):
        if clean_config is None:
            clean_config = []
        self.document_store = document_store
        self.nested_vector_field = nested_vector_field
        self.clean_config = clean_config

    def run(
        self,
        query: Optional[str] = None,
        file_paths: Optional[List[str]] = None,
        labels: Optional[MultiLabel] = None,
        documents: Optional[List[Document]] = None,
        meta: Optional[dict] = None,
        hits: Optional[List[any]] = [],
        params: Optional[dict] = None,
        elasticsearch_result: Any = None,
    ):
#        import pdb; pdb.set_trace()
        try:
            hits = elasticsearch_result["hits"]["hits"]
        except KeyError:
            hits = []

        documents = []
        content_field = self.document_store.content_field
        nested_content_field = self.document_store.nested_content_field
        embedding_field = self.document_store.embedding_field
        nested_vector_field = self.nested_vector_field

        for hit in hits:
            try:
                inner_hits = hit["inner_hits"][nested_vector_field]["hits"]["hits"]
                assert len(inner_hits) > 0
            except (KeyError, AssertionError, TypeError):

                # Filtering empty documents
                if hit["_source"].get(content_field):
                    hit["_source"][content_field] = clean_text(
                        text=hit["_source"][content_field], conf=self.clean_config
                    )

                    documents.append(hit)

                # TODO: here we need to split docs by sizes
                continue

            for inner_hit in inner_hits:
                if inner_hit["_source"].get(nested_content_field):
                    doc = deepcopy(hit)
                    doc["_source"][embedding_field] = inner_hit["_source"][
                        embedding_field
                    ]
                    doc["_source"][nested_content_field] = clean_text(
                        text=inner_hit["_source"][nested_content_field],
                        conf=self.clean_config,
                    )
                    documents.append(doc)

        # Adjust the query for the following pipeline node, the AnswerExtraction
        if not isinstance(query, str):
            try:
                query = params["payload"]["RawRetriever"]["payload"]["custom_query"]
            except KeyError:
                try:
                    body = params["payload"]["query"]
                    query = get_search_term(body)
                except Exception:
                    logger.exception("Could not get custom query from RawRetriever")
                    # import pdb

                    # pdb.set_trace()
                    query = ""

        res = {
            "documents": [
                self.document_store._convert_es_hit_to_document(
                    raw_doc, return_embedding=False
                )
                for raw_doc in documents
            ],
            "query": query,
        }
        return res, "output_1"
