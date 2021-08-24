import os

import pkg_resources
import yaml
from haystack.schema import BaseComponent

APP_VERSION = "0.0.1"
APP_NAME = "EEA SemanticSearch NLPService"
API_PREFIX = "/api"

# haystack config
PIPELINE_YAML_PATH = os.getenv(
    "PIPELINE_YAML_PATH",
    pkg_resources.resource_filename("app", "../pipeline/pipelines.yml"),
)

IS_DEBUG = os.getenv("DEBUG", True)
QUERY_PIPELINE_NAME = os.getenv("QUERY_PIPELINE_NAME", "query")
SEARCH_PIPELINE_NAME = os.getenv("QUERY_PIPELINE_NAME", "search")
INDEXING_PIPELINE_NAME = os.getenv("INDEXING_PIPELINE_NAME", "indexing")
QUESTION_PIPELINE_NAME = os.getenv("QUERY_PIPELINE_NAME", "question")

FILE_UPLOAD_PATH = os.getenv("FILE_UPLOAD_PATH", "./file-upload")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ROOT_PATH = os.getenv("ROOT_PATH", "/")

CONCURRENT_REQUEST_PER_WORKER = int(
    os.getenv("CONCURRENT_REQUEST_PER_WORKER", 4))

conf = None

with open(PIPELINE_YAML_PATH, "r", encoding='utf-8') as stream:
    conf = yaml.safe_load(stream)


def load_components(data):
    components = {}  # definitions of each component from the YAML.

    for definition in data["components"]:
        name = definition.pop("name")
        params = definition.get('params', {})

        # loads references to other components
        for k, v in params.items():
            if isinstance(v, str) and v in components:
                params[k] = components[v]

        components[name] = BaseComponent.load_from_args(
            definition['type'], **params
        )

    return components


components = load_components(conf)
