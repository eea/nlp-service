import logging
from typing import Dict, List, Optional

from haystack import Document
from haystack.nodes.summarizer import TransformersSummarizer

logger = logging.getLogger(__name__)


class SearchlibTransformersSummarizer(TransformersSummarizer):
    """Transformers summarizer"""

    def run(
        self,
        documents: List[Document],
        generate_single_summary: Optional[bool] = None,
        max_length: int = 500,
        min_length: int = 50,
        truncation: bool = True,
    ):  # type: ignore

        results: Dict = {"documents": []}

        if documents:
            results["documents"] = self.predict(
                documents=documents,
                generate_single_summary=generate_single_summary,
                max_length=max_length,
                min_length=min_length,
                truncation=truncation,
            )

        return results, "output_1"

    def predict(
        self,
        documents: List[Document],
        generate_single_summary: Optional[bool] = None,
        max_length: int = 500,
        min_length: int = 50,
        truncation: bool = True,
    ) -> List[Document]:
        """
        Produce the summarization from the supplied documents.
        These document can for example be retrieved via the Retriever.

        :param documents: Related documents (e.g. coming from a retriever) that the answer shall be conditioned on.
        :param generate_single_summary: Whether to generate a single summary for all documents or one summary per document.
                                        If set to "True", all docs will be joined to a single string that will then
                                        be summarized.
                                        Important: The summary will depend on the order of the supplied documents!
        :param truncation: Truncate to a maximum length accepted by the model
        :return: List of Documents, where Document.text contains the summarization and Document.meta["context"]
                 the original, not summarized text
        """

        if self.min_length > self.max_length:
            raise AttributeError("min_length cannot be greater than max_length")

        if len(documents) == 0:
            raise AttributeError(
                "Summarizer needs at least one document to produce a summary."
            )

        if generate_single_summary is None:
            generate_single_summary = self.generate_single_summary

        contexts: List[str] = [doc.content for doc in documents]

        if generate_single_summary:
            # Documents order is very important to produce summary.
            # Different order of same documents produce different summary.
            contexts = [self.separator_for_single_summary.join(contexts)]

        encoded_input = self.summarizer.tokenizer(contexts, verbose=False)
        for input_id in encoded_input["input_ids"]:
            tokens_count: int = len(input_id)
            if tokens_count > self.summarizer.tokenizer.model_max_length:
                truncation_warning = (
                    "One or more of your input document texts is longer than the specified "
                    f"maximum sequence length for this summarizer model. "
                    f"Generating summary from first {self.summarizer.tokenizer.model_max_length}"
                    f" tokens."
                )
                if truncation_warning not in self.print_log:
                    logger.warning(truncation_warning)
                    self.print_log.add(truncation_warning)

        summaries = self.summarizer(
            contexts,
            min_length=min_length,
            max_length=max_length,
            return_text=True,
            clean_up_tokenization_spaces=self.clean_up_tokenization_spaces,
            truncation=True,
        )

        result: List[Document] = []

        for context, summarized_answer in zip(contexts, summaries):
            cur_doc = Document(
                content=summarized_answer["summary_text"], meta={"context": context}
            )
            result.append(cur_doc)

        return result

    #
    # def run_batch(self, *args, **kwargs):
    #     # TODO: implement this
    #     raise ValueError
    #     return {}, "output_1"
