from app.core.config import SUMMARIZER_PIPELINE_NAME
from app.core.model import register_model
from app.core.pipeline import PipelineModel
from haystack.schema import Document


@register_model("summarizer_model")
class SummarizerModel(PipelineModel):
    pipeline_name = SUMMARIZER_PIPELINE_NAME

    def _pre_process(self, payload):
        return {"documents": [Document(payload.query)]}

    def _post_process(self, prediction):
        docs = prediction['documents']
        answer = "\n".join(doc.text for doc in docs)

        return {"answer": answer}
