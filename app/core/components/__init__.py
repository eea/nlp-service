# import haystack.ranker  # noqa // register these components

from .embedding import EmbeddingModel
from .searchlib.documentstore import SearchlibElasticsearchDocumentStore
from .searchlib.querysearch import QuerySearchModel
from .searchlib.question import (Category, DPRequestClassifier,
                                 ElasticSearchRequestClassifier)
# from .searchlib.ranker import RawFARMRanker
from .searchlib.reader import SearchlibQAAdapter
from .searchlib.retriever import (RawDensePassageRetriever,
                                  RawElasticsearchRetriever)
from .spacy import SpacyModel
from .split import Split
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
    DPRequestClassifier,
    SearchlibQAAdapter,
    SearchlibTransformersSummarizer,
    SearchlibElasticsearchDocumentStore,
    SentenceTransformer,
    SpacyModel,
    TransformersPipeline,
    QuerySearchModel,
    Split,
]
