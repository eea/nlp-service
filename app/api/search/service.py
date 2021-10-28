from app.core.model import register_model
from app.core.pipeline import PipelineModel


@register_model("search")
class SearchModel(PipelineModel):
    pipeline_name = "search"

    def predict(self, payload):
        body = payload.dict()
        body.update(body.get('params', {}) or {})
        result = self.pipeline.run(params={'payload': body})
        es = result.pop('elasticsearch_result')
        result.update(es)
        return result
