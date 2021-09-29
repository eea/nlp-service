from copy import deepcopy
from haystack.document_store import ElasticsearchDocumentStore
from typing import List, Optional, Any       # , Dict
from haystack.schema import Document
import numpy as np
import logging
from elasticsearch.exceptions import RequestError
import json

logger = logging.getLogger(__name__)


class SearchlibElasticsearchDocumentStore(ElasticsearchDocumentStore):
    def query(
        self,
        query: Optional[dict],
        aggs: Optional[dict] = None,
        highlight: Optional[dict] = None,
        size: Optional[int] = None,
        sort: Optional[Any] = None,
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

        if sort is not None:
            body['sort'] = sort

        # print(json.dumps(body))
        logger.debug(f"Retriever query: {body}")

        result = self.client.search(index=index, body=body)

        return result

    def _get_vector_similarity_query(self, body: dict, query_emb: np.ndarray):
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
        # QUERY_MATCH_ALL = jq.compile(
        #     '.function_score.query.bool.must[].match_all')
        # QUERY_MATCH_TEXT = jq.compile(
        #     '.function_score.query.bool.must[].multi_match.query')
        # search_term = compiled.input(body).first()

        if query.get('function_score', {}).get(
                'query', {}).get('bool', {}).get('must'):
            # TODO: might not be enough, might be too much
            del query['function_score']['query']['bool']['must']

        filterquery = query.get('function_score', {}).get('query')

        script = {
            "script_score": {
                "query": filterquery or {"match_all": {}},
                "script": {
                    # offset score to ensure a positive range as required by ES
                    "source": f"{similarity_fn_name}(params.query_vector,"
                    f"'{self.embedding_field}') + 1000",
                    "params": {"query_vector": query_emb.tolist()},
                },
            }
        }
        query['function_score']['query'] = script
        print('---------')
        print(query)
        print('---------')
        return query

    def query_by_embedding(self,
                           query_emb: np.ndarray,
                           return_embedding: Optional[bool] = None,

                           aggs: Optional[dict] = None,
                           highlight: Optional[dict] = None,
                           index: Optional[str] = None,
                           query: Optional[dict] = None,
                           size: Optional[int] = None,
                           sort: Optional[Any] = None,
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

            if size is not None:
                body['size'] = size

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
                    body=body, request_timeout=300)
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
