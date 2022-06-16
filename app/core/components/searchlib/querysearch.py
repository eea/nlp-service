from haystack.nodes.base import BaseComponent

_default_query_types = [
    "query:interrogative",
    "query:declarative",
    # 'query:keyword',
    # 'request:query', // temporary
]


class QuerySearchModel(BaseComponent):
    """A component that only serves as a vesel for configuration from yml files"""

    def __init__(
        self,
        search_pipeline,
        qa_pipeline,
        excluded_meta_data=None,
        default_query_types=None,
    ):
        self.search_pipeline = search_pipeline
        self.qa_pipeline = qa_pipeline
        self.excluded_meta_data = excluded_meta_data or []

        if default_query_types is None:
            default_query_types = _default_query_types

        self.default_query_types = default_query_types

    def run(self, payload):
        return
