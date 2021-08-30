from pathlib import Path

import click


def run_pipeline(pipeline_name, request):
    """ Run a pipeline from the command line
    """
    from app.core.config import PIPELINE_YAML_PATH
    from haystack import Pipeline
    pipeline = Pipeline.load_from_yaml(
        Path(PIPELINE_YAML_PATH), pipeline_name=pipeline_name
    )
    result = pipeline.run(**request)
    return result


@click.command()
@click.argument('index')
@click.argument('textfield')
@click.argument('embeddingfield')
@click.option('--host', default='localhost')
@click.option('--port', default='9200')
def dpr_processing_pipeline(index, textfield, embeddingfield, host, port):  # ,
    from haystack.document_store.elasticsearch import \
        ElasticsearchDocumentStore
    from haystack.retriever.dense import DensePassageRetriever
    from loguru import logger

    elastic = ElasticsearchDocumentStore(
        host=host,
        port=port,
        index=index,
        create_index=False,
        text_field=textfield,       # all_fields_for_freetext
        embedding_field=embeddingfield,  # description_embedding
        # index="global-search", create_index=False,
        # text_field="description",
    )
    retriever = DensePassageRetriever(elastic)
    elastic.update_embeddings(retriever=retriever)

    logger.info("Done updating embeddings")


if __name__ == "__main__":
    dpr_processing_pipeline()
