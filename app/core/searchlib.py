from haystack import BaseComponent


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
