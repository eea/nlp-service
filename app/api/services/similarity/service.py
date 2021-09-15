import torch
from app.core.model import register_model
from app.core.pipeline import PipelineModel, process_request
from haystack import Document
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
        documents = [Document(text) for text in sentences]

        output = process_request(
            self.pipeline, {'documents': documents})

        documents = output['documents']

        base_doc = documents[0]
        del documents[0]

        predictions = []
        for i, doc in enumerate(documents):
            score = self.cos_sim(base_doc.embedding, doc.embedding)
            predictions.append({'score': score, "text": doc.text})

        return {"base": base_doc.text, "predictions": predictions}
