from pathlib import Path

import click
from elasticsearch import Elasticsearch  # , RequestsHttpConnection


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
def dpr_processing_pipeline(index, textfield, embeddingfield, host, port):
    from haystack.document_store.elasticsearch import \
        ElasticsearchDocumentStore
    from haystack.retriever.dense import DensePassageRetriever
    from loguru import logger

    client = Elasticsearch(hosts=[host], scheme='http', timeout=300)
    client.indices.put_mapping({
        "properties": {
            embeddingfield: {
                "type": "dense_vector",
                "dims": 768     # default in ElasticsearchDocumentStore
            }
        }
    }, index=index)

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
    retriever = DensePassageRetriever(
        elastic,
        query_embedding_model="facebook/dpr-question_encoder-single-nq-base",
        passage_embedding_model="facebook/dpr-ctx_encoder-single-nq-base",
        max_seq_len_query=64,
        max_seq_len_passage=256,
        batch_size=16,
        use_gpu=True,
        embed_title=False,
        use_fast_tokenizers=True
    )

    elastic.update_embeddings(retriever=retriever)

    logger.info("Done updating embeddings")


if __name__ == "__main__":
    dpr_processing_pipeline()
