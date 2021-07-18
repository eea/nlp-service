from app.core.config import components
from app.core.model import register_model
from app.core.pipeline import Pipeline
from haystack.pipeline import DocumentSearchPipeline


@register_model("search")
class SearchModel(Pipeline):
    def __init__(self):
        retriever = components['ESRetriever']
        self.pipeline = DocumentSearchPipeline(retriever=retriever)
