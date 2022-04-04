import haystack.ranker  # noqa // register these components

from .embedding import EmbeddingModel
from .feedback import FeedbackModel
from .searchlib.documentstore import SearchlibElasticsearchDocumentStore
from .searchlib.question import Category, ElasticSearchRequestClassifier
# from .searchlib.ranker import RawFARMRanker
from .searchlib.reader import SearchlibQAAdapter
from .searchlib.retriever import (RawDensePassageRetriever,
                                  RawElasticsearchRetriever)
from .spacy import SpacyModel
from .summarizer import SearchlibTransformersSummarizer
from .transformer import (NERTransformersPipeline, SentenceTransformer,
                          TransformersPipeline)

__all__ = [
    Category,
    ElasticSearchRequestClassifier,
    EmbeddingModel,
    NERTransformersPipeline,
    RawDensePassageRetriever,
    RawElasticsearchRetriever,
    # RawFARMRanker,
    SearchlibQAAdapter,
    SearchlibTransformersSummarizer,
    SearchlibElasticsearchDocumentStore,
    SentenceTransformer,
    SpacyModel,
    TransformersPipeline,
    FeedbackModel,
]
