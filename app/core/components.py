from haystack.schema import BaseComponent


class TransformersPipeline(BaseComponent):
    def __init__(self, *args, **kwargs):
        from transformers import pipeline
        self.pipeline = pipeline(*args, **kwargs)

    def run(self, *args, **kwargs):
        payload = kwargs.get('payload', {})
        result = self.pipeline(**payload)
        return result, 'output_1'


class SentenceTransformer(BaseComponent):
    def __init__(self, *args, **kwargs):
        # from sentence_transformers import SentenceTransformer
        # self.model = SentenceTransformer(kwargs['model'])
        import torch

        self.torch = torch
        from transformers import AutoModel, AutoTokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(kwargs['model'])
        self.model = AutoModel.from_pretrained(kwargs['model'])

    def run(self, *args, **kwargs):
        sentences = kwargs.get('sentences', [])
        encoded_input = self.tokenizer(sentences, padding=True,
                                       truncation=True, return_tensors='pt')
        with self.torch.no_grad():
            model_output = self.model(**encoded_input)

        embeddings = self._cls_pooling(
            model_output, encoded_input['attention_mask'])

        result = list(zip(sentences, embeddings))
        return result, 'output_1'

    def _cls_pooling(self, model_output, attention_mask):
        return model_output[0][:, 0]


class SearchlibQAAdapter(BaseComponent):

    def run(self, **kwargs):
        # @(Pdb) pp kwargs['answers'][0]
        # {'answer': 'global warming and a rapidly evolving world economy',
        #  'context': 't local level are exacerbated by threats by global '
        #  'document_id': 'http://www.eea.europa.eu/themes/challenges',
        #  'meta': {'SearchableText':

        answers = kwargs.pop('answers', [])
        output = {**kwargs, "answers": answers}

        for doc in answers:     # in-place mutation
            meta = doc.pop('meta', {})
            doc['source'] = meta
            doc['id'] = doc['document_id']

        return output, 'output_1'


class Category(BaseComponent):

    def __init__(self, *args, **kwargs):
        self.category = kwargs.get('category', 'untitled')

    def run(self, **kwargs):
        return {"category": self.category}, 'output_1'
