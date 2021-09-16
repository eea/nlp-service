from app.core.config import components
from app.core.model import register_model
from app.core.pipeline import PipelineModel


@register_model("search")
class SearchModel(PipelineModel):
    def __init__(self):
        from haystack.pipeline import DocumentSearchPipeline
        self.retriever = components['ESRetriever']
        self.pipeline = DocumentSearchPipeline(retriever=self.retriever)

    def predict(self, payload):
        res = self.pipeline.run(**dict(payload))
        return res
