import click
from loguru import logger

# from elasticsearch import Elasticsearch  # , RequestsHttpConnection


@click.command()
@click.argument('input_index')
@click.argument('input_text_field')
@click.argument('output_index')
@click.option('--split-length', default=100)
@click.option('--host', default='localhost')
@click.option('--port', default='9200')
def preprocess(input_index,
               input_text_field, output_index, split_length, host, port):
    """
    A pipeline that takes an ElasticSearch index and pipes it to another
    destination index, converted as Haystack documents with DPR passage
    embeddings
    """

    from haystack.document_store.elasticsearch import \
        ElasticsearchDocumentStore
    from haystack.schema import Document
    from haystack.preprocessor import PreProcessor

    preprocessor = PreProcessor(split_length=split_length)

    # client = Elasticsearch(hosts=[host], scheme='http', timeout=300)

    input_store = ElasticsearchDocumentStore(
        host=host,
        port=port,
        index=input_index,
        create_index=True,
    )

    to_index = []
    BLACKLIST = ['id']

    for doc in input_store.get_all_documents_generator():
        logger.info(f"Indexing {doc.id}")

        # if (isinstance(doc.text, list)):
        #     text = "\n".join(doc.text)
        # elif doc.text is None:
        #     text = ""
        # else:
        #     text = doc.text
        text = doc.meta[input_text_field]
        meta = {k: v
                for k, v in doc.meta.items() if k not in BLACKLIST}

        inputdoc = {"text": text}
        res = preprocessor.process(inputdoc)
        for d in res:
            # d['id'] = f"{d['meta']['about']}#{d['meta']['_split_id']}"
            d.update(meta)
            to_index.append(d)

    output_store = ElasticsearchDocumentStore(
        host=host,
        port=port,
        index=output_index,
        create_index=True,
    )
    output_store.write_documents(to_index)

    logger.info("Done.")


if __name__ == "__main__":
    preprocess()
