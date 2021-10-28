from app.core.config import QUESTION_PIPELINE_NAME
from app.core.messages import NO_VALID_PAYLOAD
from app.core.model import register_model
from app.core.pipeline import PipelineModel

from .api import QuestionRequest, QuestionResponse


@register_model("QUESTION_CLASSIFIER")
class QuestionModel(PipelineModel):
    pipeline_name = QUESTION_PIPELINE_NAME

    def _post_process(self, prediction):
        # output_1 is Question
        # output_2 is Keyword
        return {"answer": prediction['query_type']}

    def predict(self, payload: QuestionRequest) -> QuestionResponse:
        if payload is None:
            raise ValueError(NO_VALID_PAYLOAD.format(payload))

        return super(QuestionModel, self).predict(payload)
