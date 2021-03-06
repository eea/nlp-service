from app.core.model import register_model
from app.core.pipeline import PipelineModel
from haystack import Document


@register_model("ner_model")
class NERClassifierModel(PipelineModel):
    pipeline_name = "ner"

    def _pre_process(self, payload):
        return {'documents': [Document(text) for text in payload.texts]}

    def _post_process(self, prediction):
        # prediction is like:
        # [{'end': 5,
        # 'entity': 'B-ORG',
        # 'index': 1,
        # 'score': 0.9973650574684143,
        # 'start': 1,
        #   'word': ''}]
        return {'entities': prediction['result']}
