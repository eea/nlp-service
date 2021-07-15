import os

import pkg_resources
from starlette.config import Config

# from starlette.datastructures import Secret

APP_VERSION = "0.0.1"
APP_NAME = "EEA SemanticSearch NLPService"
API_PREFIX = "/api"

config = Config(".env")

IS_DEBUG: bool = config("IS_DEBUG", cast=bool, default=False)
DEFAULT_MODEL_PATH: str = config("DEFAULT_MODEL_PATH")

# haystack config
PIPELINE_YAML_PATH = os.getenv(
    "PIPELINE_YAML_PATH", pkg_resources.resource_filename(
        "app", "../pipeline/pipelines.yml"))

QUERY_PIPELINE_NAME = os.getenv("QUERY_PIPELINE_NAME", "query")
INDEXING_PIPELINE_NAME = os.getenv("INDEXING_PIPELINE_NAME", "indexing")

FILE_UPLOAD_PATH = os.getenv("FILE_UPLOAD_PATH", "./file-upload")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ROOT_PATH = os.getenv("ROOT_PATH", "/")

CONCURRENT_REQUEST_PER_WORKER = int(
    os.getenv("CONCURRENT_REQUEST_PER_WORKER", 4))
