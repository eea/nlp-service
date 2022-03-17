import logging

from haystack.nodes.base import BaseComponent
from spacy.lang.en import English

logger = logging.getLogger(__name__)
# import spacy


class SearchlibQAAdapter(BaseComponent):
    def __init__(self):
        # self.nlp = spacy.load("en_core_web_trf")
        nlp = English()
        nlp.add_pipe("sentencizer")
        self.nlp = nlp

    def run(self, query, documents, answers):
        # @(Pdb) pp kwargs['answers'][0]
        # {'answer': 'global warming and a rapidly evolving world economy',
        #  'context': 't local level are exacerbated by threats by global '
        #  'document_id': 'http://www.eea.europa.eu/themes/challenges',
        #  'meta': {'SearchableText':

        # answers = kwargs.pop('answers', [])

        document_map = {doc.id: doc for doc in documents}

        output = {
            "documents": documents,
            "answers": [],
        }

        for doc in [a.to_dict() for a in answers if a.answer]:  # in-place mutation
            meta = doc.pop("meta", {})
            doc["source"] = meta
            doc["id"] = doc["document_id"]
            if not doc["id"]:
                logger.debug("Skipping an unknown document")
                continue
            doc["text"] = document_map[doc["id"]].content
            sdoc = self.nlp(doc["text"])
            span = doc["offsets_in_document"][0]
            start = span["start"]
            end = span["end"]

            answer_span = sdoc.char_span(
                start,
                end
                # doc["offset_start_in_doc"], doc["offset_end_in_doc"]
            )

            if answer_span is None:
                continue

            current_sent = answer_span.sent

            try:
                sentences = list(sdoc.sents)
            except Exception:
                logger.exception("Error in Searchlib QA Adapter")
                continue
            index = -1
            for i, sent in enumerate(sentences):
                if sent == current_sent:
                    index = i

            # TODO: there's a bug here in case the answer is multiple sentences.

            s = index > 0 and index - 1 or 0
            e = index == len(sentences) - 1 and len(sentences) - 1 or index + 1
            full_context = sentences[s:e]

            doc["offset_start"] = start
            doc["offset_end"] = end
            doc["full_context"] = " ".join([s.text for s in full_context])

            if not (start or end):
                continue

            output["answers"].append(doc)

        return output, "output_1"
