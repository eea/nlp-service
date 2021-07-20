from app.core.config import QUERY_PIPELINE_NAME
from app.core.model import register_model
from app.core.pipeline import PipelineModel
from app.data_models.qa import QA_Request, Response


@register_model("qa")
class QAModel(PipelineModel):
    pipeline_name = QUERY_PIPELINE_NAME

    def predict(self, payload: QA_Request) -> Response:
        return super(QAModel, self).predict(payload)
