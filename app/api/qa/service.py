from app.core.config import DP_QUERY_PIPELINE_NAME, QUERY_PIPELINE_NAME
from app.core.model import register_model
from app.core.pipeline import PipelineModel


@register_model("qa")
class QAModel(PipelineModel):
    pipeline_name = QUERY_PIPELINE_NAME

    def _pre_process(self, payload):
        return {'params': {'payload': payload.dict()}}


@register_model("dp_qa")
class QADPModel(PipelineModel):
    pipeline_name = DP_QUERY_PIPELINE_NAME

    def _pre_process(self, payload):
        body = payload.dict()
        params = body.pop('params') or {}
        if not params.get('query'):
            params['query'] = body['query']
        return {'params': {'payload': params}}
