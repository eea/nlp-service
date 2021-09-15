from haystack.schema import BaseComponent


class SpacyModel(BaseComponent):
    def __init__(self, *args, **kwargs):
        import spacy
        self.spacy = spacy
        model = kwargs.get('model', 'en_core_web_trf')  # Transformers model
        # for NER pipeline set disable to:
        # ["tagger", "parser", "attribute_ruler", "lemmatizer"]
        disable = kwargs.get('disable', [])
        self.nlp = spacy.load(model, disable=disable)

    def run(self, documents):
        return {"spacy_documents":
                [self.nlp(doc.text) for doc in documents]}, 'output_1'


class EmbeddingModel(BaseComponent):
    def __init__(self, *args, **kwargs):
        from haystack import Document
        from haystack.retriever.dense import DensePassageRetriever

        self.Document = Document
        self.model = DensePassageRetriever(**kwargs)

    def run(self, payload):
        result = None

        if payload['is_passage']:
            documents = [self.Document(s) for s in payload['snippets']]
            result = self.model.embed_passages(documents)
        else:
            result = self.model.embed_queries(payload['snippets'])

        return {"embeddings": result}, 'output_1'


class TransformersPipeline(BaseComponent):
    def __init__(self, *args, **kwargs):
        from transformers import pipeline
        self.pipeline = pipeline(*args, **kwargs)

    def run(self, meta):
        payload = meta['payload']
        result = self.pipeline(**payload)
        return {"result": result}, 'output_1'


class NERTransformersPipeline(TransformersPipeline):
    def __init__(self, *args, **kwargs):
        super(NERTransformersPipeline, self).__init__(*args, **kwargs)

        from transformers import AutoTokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(kwargs['model'])

    def run(self, documents):
        # See https://huggingface.co/transformers/usage.html#named-entity-recognition
        payload = {"inputs": [doc.text for doc in documents]}

        result, output = super(NERTransformersPipeline,
                               self).run({'payload': payload})
        # Result is like:
        # [{'end': 5,
        #     'entity': 'B-ORG',
        #     'index': 1,
        #     'score': 0.9973650574684143,
        #     'start': 1,
        #     'word': 'ĠApple'}]
        for entry in result['result']:
            entry['word'] = self.tokenizer\
                .convert_tokens_to_string([entry['word']]).strip()
            entry['score'] = float(entry['score'])
            entry['start'] = int(entry['start'])
            entry['end'] = int(entry['end'])

        return {"result": result['result']}, output


class SentenceTransformer(BaseComponent):
    def __init__(self, *args, **kwargs):
        # from sentence_transformers import SentenceTransformer
        # self.model = SentenceTransformer(kwargs['model'])
        import torch

        self.torch = torch
        from transformers import AutoModel, AutoTokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(kwargs['model'])
        self.model = AutoModel.from_pretrained(kwargs['model'])

    def run(self, documents):
        sentences = [doc.text for doc in documents]
        encoded_input = self.tokenizer(sentences, padding=True,
                                       truncation=True, return_tensors='pt')
        with self.torch.no_grad():
            model_output = self.model(**encoded_input)

        embeddings = self._cls_pooling(
            model_output, encoded_input['attention_mask'])

        for doc, embedding in zip(documents, embeddings):
            doc.embedding = embedding

        return {'documents': documents}, 'output_1'

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


class Category(BaseComponent):

    def __init__(self, *args, **kwargs):
        self.category = kwargs.get('category', 'untitled')

    def run(self, **kwargs):
        return {"category": self.category}, 'output_1'


# class SearchlibQAAdapter(BaseComponent):
#
#     def run(self, query, documents, answers):
#         import pdb
#         pdb.set_trace()
#         # @(Pdb) pp kwargs['answers'][0]
#         # {'answer': 'global warming and a rapidly evolving world economy',
#         #  'context': 't local level are exacerbated by threats by global '
#         #  'document_id': 'http://www.eea.europa.eu/themes/challenges',
#         #  'meta': {'SearchableText':
#
#         answers = kwargs.pop('answers', [])
#         output = {**kwargs, "answers": answers}
#
#         for doc in answers:     # in-place mutation
#             meta = doc.pop('meta', {})
#             doc['source'] = meta
#             doc['id'] = doc['document_id']
#
#         return output, 'output_1'
