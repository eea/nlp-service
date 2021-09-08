from app.core.model import register_model
from app.core.pipeline import PipelineModel


@register_model("ner_model")
class NERClassifierModel(PipelineModel):
    pipeline_name = "ner"

    def _pre_process(self, payload):
        # See https://huggingface.co/transformers/usage.html#named-entity-recognition
        return {'payload': {"inputs": [payload.text]}}

    def _post_process(self, prediction):
        # prediction is like:
        # [{'end': 5,
        # 'entity': 'B-ORG',
        # 'index': 1,
        # 'score': 0.9973650574684143,
        # 'start': 1,
        #   'word': ''}]
        return {'entities': prediction}
