from app.core.model import register_model
from app.core.pipeline import PipelineModel, process_request


@register_model("embedding_model")
class PassageEmbeddingModel(PipelineModel):
    pipeline_name = "embedding"

    def _predict(self, payload):
        # See https://www.sbert.net/docs/usage/semantic_textual_similarity.html
        processed = process_request(
            self.pipeline,
            {"params": {"EmbeddingModel": {'payload': payload}}}
        )

        out = []
        for (text, tensor) in zip(payload['snippets'],
                                  processed['embeddings']):
            out.append({'text': text, "embedding": tensor.flatten().tolist()})

        return {"embeddings": out}


# class BaseEmbedder(object):
#
#     def _predict(self, payload):
#         # See https://www.sbert.net/docs/usage/semantic_textual_similarity.html
#         import pdb
#         pdb.set_trace()
#         embeddings = process_request(
#             self.pipeline, {'sentences': payload['phrases']})
#
#         out = []
#         for (text, tensor) in embeddings:
#             out.append({'text': text, "embedding": tensor})
#         return {"embeddings": out}
#
#
# @register_model("sentence_embedding_model")
# class SentenceEmbeddingModel(BaseEmbedder, PipelineModel):
#     pipeline_name = "sentence-embedding"
#
#
# @register_model("passage_embedding_model")
# class PassageEmbeddingModel(BaseEmbedder, PipelineModel):
#     pipeline_name = "passage-embedding"
