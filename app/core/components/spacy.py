from haystack.nodes.base import BaseComponent


class SpacyModel(BaseComponent):
    def __init__(self, *args, **kwargs):
        import spacy

        self.spacy = spacy

        model = kwargs.get("model_name_or_path", "en_core_web_trf")

        # for NER pipeline set disable to:
        # ["tagger", "parser", "attribute_ruler", "lemmatizer"]
        disable = kwargs.get("disable", [])
        self.nlp = spacy.load(model, disable=disable)

    def run(self, documents):
        return {
            "spacy_documents": [self.nlp(doc.content) for doc in documents]
        }, "output_1"
