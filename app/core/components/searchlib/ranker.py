from pathlib import Path
from typing import Any, List, Optional, Union

from haystack.nodes.document_store.base import BaseDocumentStore
from haystack.ranker import FARMRanker


class RawFARMRanker(FARMRanker):
    document_store: BaseDocumentStore

    def __init__(
        self,
        document_store: Union[str, Path],
        model_name_or_path: Union[str, Path],
        model_version: Optional[str] = None,
        batch_size: int = 50,
        use_gpu: bool = True,
        top_k: int = 10,
        num_processes: Optional[int] = None,
        max_seq_len: int = 256,
        progress_bar: bool = True,
    ):
        super(RawFARMRanker, self).__init__(
            model_name_or_path=model_name_or_path,
            model_version=model_version,
            batch_size=batch_size,
            use_gpu=use_gpu,
            top_k=top_k,
            num_processes=num_processes,
            max_seq_len=max_seq_len,
            progress_bar=progress_bar,
        )
        self.set_config(document_store=document_store)
        self.document_store = document_store

    def run(
        self,
        elasticsearch_result: Any,
        params: Optional[dict],
        query: str = "",
    ) -> dict:

        self.query_count += 1
        hits = elasticsearch_result.get("hits", {}).get("hits", [])

        if hits:
            predict = self.timing(self.predict, "query_time")
            ranked_hits = predict(query=query, params=params, hits=hits)
            elasticsearch_result["hits"]["hits"] = ranked_hits

        return {"elasticsearch_result": elasticsearch_result}, "output_1"

    def predict(
        self, query: Optional[str], hits: List[Any], params: Optional[dict]
    ) -> dict:
        """
        Use loaded ranker model to re-rank the supplied list of ES Hits.
        """

        # calculate similarity of query and each document
        documents = [
            self.document_store._convert_es_hit_to_document(
                hit, adapt_score_for_embedding=True, return_embedding=False
            )
            for hit in hits
        ]
        hit_map = {hit["_id"]: hit for hit in hits}

        query_and_docs = [{"text": (query, doc.text)} for doc in documents]

        result = self.inferencer.inference_from_dicts(dicts=query_and_docs)
        similarity_scores = [
            pred["probability"] if pred["label"] == "1" else (1 - pred["probability"])
            for preds in result
            for pred in preds["predictions"]
        ]

        # rank documents according to scores
        sorted_scores_and_documents = sorted(
            zip(similarity_scores, documents),
            key=lambda similarity_document_tuple: similarity_document_tuple[0],
            reverse=True,
        )
        sorted_hits = [hit_map[doc.id] for _, doc in sorted_scores_and_documents]
        for i, (score, _) in enumerate(sorted_scores_and_documents):
            sorted_hits[i]["ranked_score"] = score

        return sorted_hits
