from app.core.model import register_model
from app.core.pipeline import PipelineModel


@register_model("spacy_ner_model")
class SpacyNERModel(PipelineModel):
    pipeline_name = 'spacy_ner'

    def _post_process(self, documents):
        return {"documents": [doc.to_json() for doc in documents]}
