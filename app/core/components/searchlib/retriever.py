import copy
import logging
from typing import Optional

from app.core.elasticsearch import get_search_term
from haystack.nodes.retriever import (DensePassageRetriever,
                                      ElasticsearchRetriever)

logger = logging.getLogger(__name__)

es_params = [
    "query",
    "size",
    "suggest",
    "sort",
    "track_total_hits",
    "runtime_mappings",
    "highlight",
    "aggs",
    "source",
    "_source",
    "from_",
    "params",  # will be removed later in code
]


def clean_body(body):
    body = copy.deepcopy(body)
    keys = list(body.keys())

    for k in keys:
        if k not in es_params:
            del body[k]

    return body


class RawElasticsearchRetriever(ElasticsearchRetriever):
    """An ElasticSearch retriever variant that just passes ES queries to ES

    Note: document_store needs to be an instance of
    SearchlibElasticsearchDocumentStore
    """

    def run(
        self,
        root_node: str,
        params: dict,
        payload: dict = {},
        index: str = None,
        top_k: int = None,
    ):
        body = payload or params["payload"]
        body = clean_body(body)

        # Support for QA-type
        body.pop("use_dp", None)
        query = body.get("query", None)
        bodyparams = body.pop("params", {}) or {}
        from_ = bodyparams.pop("from_", 0)
        _source = bodyparams.pop("source", None) or bodyparams.pop("_source", None)

        if top_k is not None:
            body["size"] = top_k

        if from_:
            body["from_"] = from_

        if _source:
            body["_source"] = _source

        custom_query = bodyparams.pop("custom_query", None)
        if custom_query:
            body["custom_query"] = custom_query  # ['query']

        if isinstance(query, str):
            body["query"] = {"match": {"fulltext": body["query"]}}

        if index:
            body["index"] = index

        if root_node == "Query":
            self.query_count += 1
            run_query_timed = self.timing(self.retrieve, "query_time")
            output = run_query_timed(**body)
            return {"elasticsearch_result": output, "query": query}, "output_1"
        else:
            raise Exception(f"Invalid root_node '{root_node}'.")

    def retrieve(self, **kwargs):
        index = kwargs.get("index", self.document_store.index)

        args = kwargs.copy()
        args["index"] = index

        return self.document_store.query(**args)


class RawDensePassageRetriever(DensePassageRetriever):
    """A DensePassageRetriever variant that doesn't follow Haystack's query model

    Note: document_store needs to be an instance of
    SearchlibElasticsearchDocumentStore
    """

    def run(
        self,
        root_node: str,
        payload: dict = {},
        params: Optional[dict] = {},
        index: str = None,
        top_k: int = None,
    ):
        body = payload or params["payload"]
        # body.pop("use_dp", None)
        body = clean_body(body)
        query = body.get("query", None)
        bodyparams = body.pop("params", {})
        _source = bodyparams.pop("source", None) or bodyparams.pop("_source", None)

        if _source:
            body["_source"] = _source

        # custom_query = body.get('custom_query', None)

        from_ = bodyparams.pop("from_", 0)

        if from_:
            body["from_"] = from_

        if top_k is not None:
            body["size"] = top_k

        # TODO: check the custom parameters are used when required

        # Support for QA-type simple query
        if isinstance(query, str):
            body["query"] = {"match": {"text": body["query"]}}

        if index:
            body["index"] = index

        if root_node == "Query":
            self.query_count += 1
            run_query_timed = self.timing(self.retrieve, "query_time")
            output = run_query_timed(
                **body,
            )
            return {"elasticsearch_result": output, "query": query}, "output_1"
        else:
            raise Exception(f"Invalid root_node '{root_node}'.")

    def retrieve(self, **kwargs):

        index = kwargs.get("index", self.document_store.index)

        args = kwargs.copy()
        args["index"] = index

        # Hardcoded for ES
        q = kwargs["query"]
        search_term = get_search_term(q)
        query_emb = self.embed_queries(texts=[search_term])[0]
        args.pop("use_dp", None)
        args["query_emb"] = query_emb

        return self.document_store.query_by_embedding(**args)
