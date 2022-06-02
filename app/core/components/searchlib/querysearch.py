from haystack.nodes.base import BaseComponent


class QuerySearchModel(BaseComponent):
    """A component that only serves as a vesel for configuration from yml files"""

    def __init__(self, search_pipeline, qa_pipeline, excluded_meta_data=None):
        self.search_pipeline = search_pipeline
        self.qa_pipeline = qa_pipeline
        self.excluded_meta_data = excluded_meta_data or []

    def run(self, payload):
        return
