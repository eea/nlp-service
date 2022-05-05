from haystack.nodes.base import BaseComponent


class QuerySearchModel(BaseComponent):
    """A component that only serves as a vesel for configuration from yml files"""

    def __init__(self, search_pipeline, qa_pipeline, *args, **kwargs):
        self.search_pipeline = search_pipeline
        self.qa_pipeline = qa_pipeline

    def run(self, payload):
        return
