from app.core.config import DP_QUERY_PIPELINE_NAME, QUERY_PIPELINE_NAME
from app.core.model import register_model
from app.core.pipeline import PipelineModel


@register_model("qa")
class QAModel(PipelineModel):
    pipeline_name = QUERY_PIPELINE_NAME

    def _pre_process(self, payload):
        body = payload.dict()
        params = body.get("params", {})

        RawRetriever = params.pop("RawRetriever", {}) or {}
        # DensePassageRetriever = params.pop("DensePassageRetriever", {}) or {}
        AnswerExtraction = params.pop("AnswerExtraction", {}) or {}

        res = {
            "params": {
                "payload": body,
                "RawRetriever": RawRetriever,
                # "DensePassageRetriever": DensePassageRetriever,
                "AnswerExtraction": AnswerExtraction,
            }
        }

        return res


@register_model("dp_qa")
class QADPModel(PipelineModel):
    pipeline_name = DP_QUERY_PIPELINE_NAME

    def _pre_process(self, payload):
        body = payload.dict()
        params = body.pop("params") or {}
        if not params.get("query"):
            params["query"] = body["query"]

        # RawRetriever = params.pop("RawRetriever", {}) or {}
        DensePassageRetriever = params.pop("DensePassageRetriever", {}) or {}
        AnswerExtraction = params.pop("AnswerExtraction", {}) or {}

        return {
            "params": {
                "payload": params,
                # "RawRetriever": RawRetriever,
                "DensePassageRetriever": DensePassageRetriever,
                "AnswerExtraction": AnswerExtraction,
            }
        }
