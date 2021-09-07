from app.core.config import DP_QUERY_PIPELINE_NAME, QUERY_PIPELINE_NAME
from app.core.model import register_model
from app.core.pipeline import PipelineModel

from .api import QA_Request, Response


@register_model("qa")
class QAModel(PipelineModel):
    pipeline_name = QUERY_PIPELINE_NAME

    def predict(self, payload: QA_Request) -> Response:
        return super(QAModel, self).predict(payload)


@register_model("dp_qa")
class QADPModel(PipelineModel):
    pipeline_name = DP_QUERY_PIPELINE_NAME

    def predict(self, payload: QA_Request) -> Response:
        return super(QADPModel, self).predict(payload)
