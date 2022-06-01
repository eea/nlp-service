import copy
import os

import pkg_resources

APP_VERSION = "0.0.1"
APP_NAME = "EEA AI NLP Server"
API_PREFIX = "/api"

# haystack config
CONFIG_YAML_PATH = os.getenv(
    "PIPELINE_YAML_PATH",
    pkg_resources.resource_filename("app", "../conf/app.yml"),
)

CONFIG_PATH = os.getenv(
    "CONFIG_PATH",
    pkg_resources.resource_filename("app", "../conf/"),
)

CONFIG_CLEAN_PATH = os.getenv(
    "CLEAN_CONFIG_PATH",
    pkg_resources.resource_filename("app", "../app/core/components/config"),
)

IS_DEBUG = os.getenv("DEBUG", True)


# pipeline names, can be overriden from env
QUERY_PIPELINE_NAME = os.getenv("QUERY_PIPELINE_NAME", "query")
# DP_QUERY_PIPELINE_NAME = os.getenv("DP_QUERY_PIPELINE_NAME", "dpquery")
SEARCH_PIPELINE_NAME = os.getenv("QUERY_PIPELINE_NAME", "search")
INDEXING_PIPELINE_NAME = os.getenv("INDEXING_PIPELINE_NAME", "indexing")
QUESTION_PIPELINE_NAME = os.getenv("QUERY_PIPELINE_NAME", "question")
SUMMARIZER_PIPELINE_NAME = os.getenv("QUERY_PIPELINE_NAME", "summarizer")

# TODO: figure out a way to determine what the best size for this is
NLP_FIELD = os.getenv("NLP_FIELD", "nlp_250")

FILE_UPLOAD_PATH = os.getenv("FILE_UPLOAD_PATH", "./file-upload")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ROOT_PATH = os.getenv("ROOT_PATH", "/")

CONCURRENT_REQUEST_PER_WORKER = int(os.getenv("CONCURRENT_REQUEST_PER_WORKER", 20))


# components = load_components(conf)


def overwrite_with_env_variables(conf: dict, component: str):
    """
    Overwrite the YAML configuration with environment variables.
    Ex: QA_ELASTICSEARCHDOCUMENTSTORE_PARAMS_HOST=elastic
    """
    config = copy.deepcopy(conf)
    definitions = config.get("components", [])
    for definition in definitions:
        env_prefix = f"{component}_{definition['name']}_params_".upper()
        for key, value in os.environ.items():
            if key.startswith(env_prefix):
                param_name = key.replace(env_prefix, "").lower()
                definition["params"][param_name] = value

    return config
