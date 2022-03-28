from app.core.model import register_model
from app.core.pipeline import PipelineModel, process_request


@register_model("embedding_model")
class PassageEmbeddingModel(PipelineModel):
    pipeline_name = "embedding"

    def _predict(self, payload):
        # See https://www.sbert.net/docs/usage/semantic_textual_similarity.html
        processed = process_request(
            self.pipeline, {"params": {"EmbeddingModel": {"payload": payload}}}
        )

        out = []
        for (text, tensor) in zip(payload["snippets"], processed["embeddings"]):
            out.append({"text": text, "embedding": tensor.flatten().tolist()})

        return {"embeddings": out}
