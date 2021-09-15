from app.core.config import DP_QUERY_PIPELINE_NAME, QUERY_PIPELINE_NAME
from app.core.model import register_model
from app.core.pipeline import PipelineModel, process_request


@register_model("qa")
class QAModel(PipelineModel):
    pipeline_name = QUERY_PIPELINE_NAME

    def _predict(self, payload):
        return process_request(self.pipeline, payload)


@register_model("dp_qa")
class QADPModel(PipelineModel):
    pipeline_name = DP_QUERY_PIPELINE_NAME

    def _predict(self, payload):
        return process_request(self.pipeline, payload)
