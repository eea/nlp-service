from app.core.model import register_model
from app.core.pipeline import PipelineModel


@register_model("search")
class SearchModel(PipelineModel):
    pipeline_name = "search"

    def predict(self, payload):
        params = payload.dict()
        return self.pipeline.run(params=params)
