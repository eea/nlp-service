from app.core.config import QUERY_PIPELINE_NAME
from app.core.model import register_model
from app.core.pipeline import PipelineModel


@register_model("qa")
class QAModel(PipelineModel):
    pipeline_name = QUERY_PIPELINE_NAME

    def _pre_process(self, payload):
        # body = payload.dict()
        params = payload.get("params", {})

        params.pop("DensePassageRetriever", {})

        RawRetriever = params.pop("RawRetriever", {}) or {}
        AnswerExtraction = params.pop("AnswerExtraction", {}) or {}

        res = {
            "params": {
                "payload": payload,
                "RawRetriever": RawRetriever,
                "AnswerExtraction": AnswerExtraction,
            }
        }

        return res


# @register_model("dp_qa")
# class QADPModel(PipelineModel):
#     pipeline_name = DP_QUERY_PIPELINE_NAME
#
#     def _pre_process(self, payload):
#         params = payload.pop("params") or {}
#         if not params.get("query"):
#             params["query"] = payload["query"]
#
#         params.pop("RawRetriever", {})
#
#         DensePassageRetriever = params.pop("DensePassageRetriever", {}) or {}
#         AnswerExtraction = params.pop("AnswerExtraction", {}) or {}
#
#         return {
#             "params": {
#                 "payload": params,
#                 "DensePassageRetriever": DensePassageRetriever,
#                 "AnswerExtraction": AnswerExtraction,
#             }
#         }
