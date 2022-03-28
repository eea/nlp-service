from haystack.nodes.base import BaseComponent


class TransformersPipeline(BaseComponent):
    def __init__(self, *args, **kwargs):
        from transformers import pipeline

        self.pipeline = pipeline(*args, **kwargs)

    def run(self, pipeline_params):
        result = self.pipeline(**pipeline_params)

        return {"result": result}, "output_1"


class NERTransformersPipeline(TransformersPipeline):
    def __init__(self, *args, **kwargs):
        super(NERTransformersPipeline, self).__init__(*args, **kwargs)

        from transformers import AutoTokenizer

        self.tokenizer = AutoTokenizer.from_pretrained(kwargs["model"])

    def run(self, documents):
        # See https://huggingface.co/transformers/usage.html#named-entity-recognition
        payload = {"inputs": [doc.content for doc in documents]}

        result, output = super(NERTransformersPipeline, self).run(payload)
        # Result is like:
        # [{'end': 5,
        #     'entity': 'B-ORG',
        #     'index': 1,
        #     'score': 0.9973650574684143,
        #     'start': 1,
        #     'word': 'ĠApple'}]

        for doc in result["result"]:
            for entry in doc:
                entry["word"] = self.tokenizer.convert_tokens_to_string(
                    [entry["word"]]
                ).strip()
                entry["score"] = float(entry["score"])
                entry["start"] = int(entry["start"])
                entry["end"] = int(entry["end"])

        return {"result": result["result"]}, output


class SentenceTransformer(BaseComponent):
    def __init__(self, *args, **kwargs):
        # from sentence_transformers import SentenceTransformer
        # self.model = SentenceTransformer(kwargs['model'])
        import torch

        self.torch = torch
        from transformers import AutoModel, AutoTokenizer

        self.tokenizer = AutoTokenizer.from_pretrained(kwargs["model"])
        self.model = AutoModel.from_pretrained(kwargs["model"])

    def run(self, documents):
        sentences = [doc.content for doc in documents]
        encoded_input = self.tokenizer(
            sentences, padding=True, truncation=True, return_tensors="pt"
        )
        with self.torch.no_grad():
            model_output = self.model(**encoded_input)

        embeddings = self._cls_pooling(model_output, encoded_input["attention_mask"])

        for doc, embedding in zip(documents, embeddings):
            doc.embedding = embedding

        return {"documents": documents}, "output_1"

    def _cls_pooling(self, model_output, attention_mask):
        return model_output[0][:, 0]

    # Mean Pooling - Take attention mask into account for correct averaging
    # def mean_pooling(self, model_output, attention_mask):
    #     # First element of model_output contains all token embeddings
    #     token_embeddings = model_output[0]
    #     input_mask_expanded = attention_mask.unsqueeze(-1)\
    #         .expand(token_embeddings.size()).float()
    #     sum_embeddings = self.torch.sum(
    #         token_embeddings * input_mask_expanded, 1)
    #     sum_mask = self.torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    #
    #     return sum_embeddings / sum_mask
