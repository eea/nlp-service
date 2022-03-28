from haystack.nodes.base import BaseComponent


class EmbeddingModel(BaseComponent):
    def __init__(self, *args, **kwargs):
        from haystack import Document
        from haystack.nodes.retriever.dense import DensePassageRetriever

        self.Document = Document
        self.model = DensePassageRetriever(**kwargs)

    def run(self, payload):
        result = None

        if payload["is_passage"]:
            documents = [self.Document(s) for s in payload["snippets"]]
            result = self.model.embed_documents(documents)
        else:
            result = self.model.embed_queries(payload["snippets"])

        return {"embeddings": result}, "output_1"
