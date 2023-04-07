import copy
import logging
from typing import Optional

from app.core.elasticsearch import get_search_term
from haystack.nodes.retriever import (DensePassageRetriever,
                                      ElasticsearchRetriever)

from .highlight import Highlight
from .utils import find_path, get_value_from_path

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
    "index",
]

nested_tpl = {
    "inner_hits": {"_source": {"excludes": ["<nlp_embedding>"]}},
    "path": "<nlp_path>",
    "query": {
        "bool": {
            "must": {
                "multi_match": {
                    "query": "<search_term>",
                    "fields": ["<nlp_text>"],
                }
            }
        }
    },
}


def clean_body(body):
    body = copy.deepcopy(body)
    keys = list(body.keys())

    for k in keys:
        if k not in es_params:
            del body[k]

    return body


def make_nested_query(query, nlp_path, nlp_text, nlp_embedding):
    (success, path) = find_path(query, "multi_match", [])
    if success:
        node = get_value_from_path(query, path)
        node["nested"] = nested_tpl
        node["nested"]["path"] = nlp_path
        node["nested"]["inner_hits"]["_source"]["excludes"] = [
            f"{nlp_path}.{nlp_embedding}"
        ]
        node["nested"]["query"]["bool"]["must"]["multi_match"] = copy.deepcopy(
            node["multi_match"]
        )
        node["nested"]["query"]["bool"]["must"]["multi_match"]["fields"] = [
            f"{nlp_path}.{nlp_text}"
        ]
        node.pop("multi_match")
    return query


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
        q_id = payload.get("q_id")
        body = payload or params["payload"]
        body = clean_body(body)

        # Support for QA-type
        body.pop("use_dp", None)
        query = body.get("query", None)
        bodyparams = body.pop("params", {}) or {}
        from_ = bodyparams.pop("from_", 0)
        #        import pdb; pdb.set_trace()
        _source = (
            bodyparams.pop("source", None)
            or bodyparams.pop("_source", None)
            or body.pop("source", None)
            or body.pop("_source", None)
        )

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
        if bodyparams.get("scope_answerextraction", False):
            body = make_nested_query(
                body,
                self.document_store.nlp_path,
                self.document_store.nested_content_field,
                self.document_store.embedding_field,
            )

        if root_node == "Query":
            self.query_count += 1
            run_query_timed = self.timing(self.retrieve, "query_time")
            output = run_query_timed(**body)

            highlight = Highlight(search_term=get_search_term(payload["query"]))
            output = highlight.adjust(output)

            query["q_id"] = q_id
            print (f'{q_id} RawElasticsearchRetriever output_hits: {output.get("hits",{}).get("total").get("value")} query: {query}')
            return {"elasticsearch_result": output, "query": query}, "output_1"
        else:
            raise Exception(f"Invalid root_node '{root_node}'.")

    def run_batch(self, *args, **kwargs):
        # TODO: implement this
        raise ValueError
        return {}, "output_1"

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
        _source = (
            bodyparams.pop("source", None)
            or bodyparams.pop("_source", None)
            or body.pop("source", None)
            or body.pop("_source", None)
        )

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

    def run_batch(self, *args, **kwargs):
        # TODO: implement this
        raise ValueError
        return {}, "output_1"

    def retrieve(self, **kwargs):

        index = kwargs.get("index", self.document_store.index)

        args = kwargs.copy()
        args["index"] = index

        # Hardcoded for ES
        q = kwargs["query"]
        search_term = get_search_term(q)
        query_emb = self.embed_queries(queries=[search_term])[0]
        args.pop("use_dp", None)
        args["query_emb"] = query_emb

        return self.document_store.query_by_embedding(**args)
