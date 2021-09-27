import haystack.ranker      # noqa // register these components

from .spacy import SpacyModel
from .embedding import EmbeddingModel
from .searchlib.documentstore import SearchlibElasticsearchDocumentStore
from .searchlib.question import Category, ElasticSearchRequestClassifier
from .searchlib.retriever import (
    RawElasticsearchRetriever, RawDensePassageRetriever)
from .searchlib.ranker import RawFARMRanker

from .transformer import (TransformersPipeline, NERTransformersPipeline,
                          SentenceTransformer)

__all__ = [
    Category,
    ElasticSearchRequestClassifier,
    EmbeddingModel,
    NERTransformersPipeline,
    RawDensePassageRetriever,
    RawElasticsearchRetriever,
    RawFARMRanker,
    SearchlibElasticsearchDocumentStore,
    SentenceTransformer,
    SpacyModel,
    TransformersPipeline,
]
