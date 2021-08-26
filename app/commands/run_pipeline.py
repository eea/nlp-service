from pathlib import Path

from app.core.config import PIPELINE_YAML_PATH
from haystack import Pipeline
from haystack.document_store.elasticsearch import ElasticsearchDocumentStore
from haystack.retriever.dense import DensePassageRetriever
from loguru import logger


def run_pipeline(pipeline_name, request):
    """ Run a pipeline from the command line
    """
    pipeline = Pipeline.load_from_yaml(
        Path(PIPELINE_YAML_PATH), pipeline_name=pipeline_name
    )
    result = pipeline.run(**request)
    return result


def dpr_processing_pipeline():
    elastic = ElasticsearchDocumentStore(
        index="global-search", create_index=False,
        text_field="description",
        embedding_field="description_embedding"
    )
    retriever = DensePassageRetriever(elastic)
    elastic.update_embeddings(retriever=retriever)

    logger.info("Done updating embeddings")


if __name__ == "__main__":
    dpr_processing_pipeline()
