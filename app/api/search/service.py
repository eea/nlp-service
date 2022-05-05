from app.core.model import register_model
from app.core.pipeline import PipelineModel


@register_model("search")
class SearchModel(PipelineModel):
    pipeline_name = "search"

    def predict(self, body):
        result = self.pipeline.run(params={"payload": body})
        es = result.pop("elasticsearch_result", {})
        result.update(es)
        return result


# @register_model("dp_search")
# class DPSearchModel(PipelineModel):
#     pipeline_name = "dp_search"
#
#     def predict(self, body):
#         result = self.pipeline.run(params={"payload": body})
#         es = result.pop("elasticsearch_result")
#         result.update(es)
#         return result
