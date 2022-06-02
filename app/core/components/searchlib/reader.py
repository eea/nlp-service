import copy
import logging

import numpy as np
import torch
from haystack import Document
from haystack.nodes.base import BaseComponent
from sklearn.cluster import AgglomerativeClustering
from spacy.lang.en import English
from torch import Tensor

logger = logging.getLogger(__name__)
# import spacy


class AnswerOptimizer(BaseComponent):
    outgoing_edges = 1

    def run(self, answers, cutoff=0.1):
        valid_answers = [a for a in answers if a.score >= cutoff and a.answer]
        primary = valid_answers and valid_answers[0] or None

        res = {"sentence_transformer_documents": []}

        if primary:
            candidates = list(
                set(a.answer for a in valid_answers if a.answer != primary and a.answer)
            )

            payload = {"base": primary.answer, "candidates": candidates}
            sentences = [payload["base"]] + payload["candidates"]
            documents = [Document(text) for text in sentences]

            res["sentence_transformer_documents"] = documents

        return res, "output_1"


class SearchlibQAAdapter(BaseComponent):
    def __init__(self):
        # self.nlp = spacy.load("en_core_web_trf")
        nlp = English()
        nlp.add_pipe("sentencizer")
        self.nlp = nlp

    def _normalize(self, a: Tensor):
        if not isinstance(a, torch.Tensor):
            a = torch.tensor(a)

        if len(a.shape) == 1:
            a = a.unsqueeze(0)

        a_norm = torch.nn.functional.normalize(a, p=2, dim=1)

        return a_norm

    def cos_sim(self, a: Tensor, b: Tensor):
        """
        Computes the cosine similarity cos_sim(a[i], b[j]) for all i and j.
        :return: Matrix with res[i][j]  = cos_sim(a[i], b[j])
        """
        a_norm = self._normalize(a)
        b_norm = self._normalize(b)

        score_tensor = torch.mm(a_norm, b_norm.transpose(0, 1))

        score = score_tensor.numpy().flatten().tolist()[0]

        return score

    def clustering(self, documents):
        if len(documents) < 2:
            return [[doc.content, 0] for doc in documents]

        embeddings = [doc.embedding for doc in documents]

        corpus = np.array([self._normalize(e).numpy().flatten() for e in embeddings])
        # corpus = np.array([e.numpy() for e in embeddings])
        # See
        # https://scikit-learn.org/stable/modules/clustering.html#hierarchical-clustering
        model = AgglomerativeClustering(
            n_clusters=None, affinity="cosine", linkage="single", distance_threshold=0.2
        )
        model.fit(corpus)
        labels = model.labels_.tolist()
        clusters = [[doc.content, label] for (doc, label) in zip(documents, labels)]
        return clusters

    def run(self, query, documents, answers, sentence_transformer_documents):
        # @(Pdb) pp kwargs['answers'][0]
        # {'answer': 'global warming and a rapidly evolving world economy',
        #  'context': 't local level are exacerbated by threats by global '
        #  'document_id': 'http://www.eea.europa.eu/themes/challenges',
        #  'meta': {'SearchableText':

        # answers = kwargs.pop('answers', [])

        base_doc = sentence_transformer_documents[0]
        del sentence_transformer_documents[0]

        predictions = []
        for i, doc in enumerate(sentence_transformer_documents):
            score = self.cos_sim(base_doc.embedding, doc.embedding)
            predictions.append({"score": score, "text": doc.content})

        similarity = {
            "base": base_doc.content,
            "predictions": predictions,
            "clusters": self.clustering([base_doc] + sentence_transformer_documents),
        }

        output = {
            "documents": documents,
            "similarity": similarity,
            "answers": [],
        }

        document_map = {doc.id: doc for doc in documents}

        for doc in [a.to_dict() for a in answers if a.answer]:  # in-place mutation
            doc["original_answer"] = copy.deepcopy(doc)
            del doc["original_answer"]["meta"]
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
