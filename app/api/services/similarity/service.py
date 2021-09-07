import torch
from app.core.model import register_model
from app.core.pipeline import PipelineModel, process_request
from torch import Tensor


@register_model("similarity_model")
class SimilarityModel(PipelineModel):
    pipeline_name = "similarity"

    def cos_sim(self, a: Tensor, b: Tensor):
        """
        Computes the cosine similarity cos_sim(a[i], b[j]) for all i and j.
        :return: Matrix with res[i][j]  = cos_sim(a[i], b[j])
        """
        if not isinstance(a, torch.Tensor):
            a = torch.tensor(a)

        if not isinstance(b, torch.Tensor):
            b = torch.tensor(b)

        if len(a.shape) == 1:
            a = a.unsqueeze(0)

        if len(b.shape) == 1:
            b = b.unsqueeze(0)

        a_norm = torch.nn.functional.normalize(a, p=2, dim=1)
        b_norm = torch.nn.functional.normalize(b, p=2, dim=1)

        return torch.mm(a_norm, b_norm.transpose(0, 1))

    def _predict(self, payload):
        # See https://www.sbert.net/docs/usage/semantic_textual_similarity.html
        sentences = [payload['base']] + payload['candidates']
        embeddings = process_request(self.pipeline, {'sentences': sentences})
        (base_text, base_embedding) = embeddings[0]
        del embeddings[0]

        predictions = []
        for i, (text, emb) in enumerate(embeddings):
            score = self.cos_sim(base_embedding, emb)
            predictions.append({'score': score, "text": text})

        return {"base": base_text, "predictions": predictions}
