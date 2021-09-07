import os

import pkg_resources

APP_VERSION = "0.0.1"
APP_NAME = "EEA SemanticSearch NLPService"
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


IS_DEBUG = os.getenv("DEBUG", True)


# pipeline names, can be overriden from env
QUERY_PIPELINE_NAME = os.getenv("QUERY_PIPELINE_NAME", "query")
DP_QUERY_PIPELINE_NAME = os.getenv("DP_QUERY_PIPELINE_NAME", "dpquery")
SEARCH_PIPELINE_NAME = os.getenv("QUERY_PIPELINE_NAME", "search")
INDEXING_PIPELINE_NAME = os.getenv("INDEXING_PIPELINE_NAME", "indexing")
QUESTION_PIPELINE_NAME = os.getenv("QUERY_PIPELINE_NAME", "question")
SUMMARIZER_PIPELINE_NAME = os.getenv("QUERY_PIPELINE_NAME", "summarizer")


FILE_UPLOAD_PATH = os.getenv("FILE_UPLOAD_PATH", "./file-upload")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ROOT_PATH = os.getenv("ROOT_PATH", "/")

CONCURRENT_REQUEST_PER_WORKER = int(
    os.getenv("CONCURRENT_REQUEST_PER_WORKER", 4))


# components = load_components(conf)
