from haystack.nodes.base import BaseComponent
from haystack.nodes.preprocessor.preprocessor import PreProcessor


class Split(BaseComponent):
    outgoing_edges = 1

    def run(self, payload):
        preprocessor = PreProcessor(
            clean_empty_lines=payload.get("clean_empty_lines", True),
            clean_whitespace=payload.get("clean_whitespace", True),
            clean_header_footer=payload.get("clean_header_footer", False),
            split_by=payload.get("split_by", "word"),
            split_length=payload.get("split_length", 5),
            split_respect_sentence_boundary=payload.get(
                "split_respect_sentence_boundary", True
            ),
            split_overlap=payload.get("split_overlap", 0),
        )
        tmp_doc = {"content": payload.get("fulltext", "")}
        docs = preprocessor.process(tmp_doc)
        return {"parts": [doc.content for doc in docs]}, "output_1"

    def run_batch(self, *args, **kwargs):
        # TODO: implement this
        raise ValueError
        return {}, "output_1"
