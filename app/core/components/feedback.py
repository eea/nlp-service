from haystack.nodes.base import BaseComponent


class FeedbackModel(BaseComponent):
    def __init__(self, *args, **kwargs):
        self.document_store = kwargs.get("document_store", None)
        import pdb

        pdb.set_trace()
        print(args)
        print(kwargs)

    def run(self, payload):
        pass
