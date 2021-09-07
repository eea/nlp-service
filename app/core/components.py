from haystack.schema import BaseComponent


class TransformersPipeline(BaseComponent):
    def __init__(self, *args, **kwargs):
        from transformers import pipeline
        self.pipeline = pipeline(*args, **kwargs)

    def run(self, *args, **kwargs):
        payload = kwargs.get('payload', {})
        result = self.pipeline(**payload)
        return result, 'output_1'


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
