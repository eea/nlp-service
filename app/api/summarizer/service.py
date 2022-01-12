from app.core.config import SUMMARIZER_PIPELINE_NAME
from app.core.model import register_model
from app.core.pipeline import PipelineModel
from haystack.schema import Document


@register_model("summarizer_model")
class SummarizerModel(PipelineModel):
    pipeline_name = SUMMARIZER_PIPELINE_NAME

    def _pre_process(self, payload):
        return {
            "documents": [Document(text) for text in payload.documents],
            "params": {
                "max_length": payload.max_length,
                "min_length": payload.min_length,
                "generate_single_summary": payload.generate_single_summary,
            },
        }
