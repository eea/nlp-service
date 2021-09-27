from app.core.model import register_model
from app.core.pipeline import PipelineModel


@register_model("search")
class SearchModel(PipelineModel):
    pipeline_name = "search"

    def predict(self, payload):
        params = payload.dict()
        result = self.pipeline.run(params={'payload': params})
        es = result.pop('elasticsearch_result')
        result.update(es)
        return result
