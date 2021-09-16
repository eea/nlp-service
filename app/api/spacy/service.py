from app.core.model import register_model
from app.core.pipeline import PipelineModel
from haystack import Document


@register_model("spacy_ner_model")
class SpacyNERModel(PipelineModel):
    pipeline_name = 'spacy_ner'

    def _pre_process(self, payload):
        return {'documents': [Document(text) for text in payload.texts]}

    def _post_process(self, prediction):
        documents = prediction['spacy_documents']
        return {"documents": [doc.to_json() for doc in documents]}
