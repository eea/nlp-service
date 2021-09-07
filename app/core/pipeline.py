import copy
import json
import time

from app.core.messages import NO_VALID_PAYLOAD
from haystack.pipeline import Pipeline
from loguru import logger

PIPELINES = {}


def add_pipeline(name, pipeline):
    PIPELINES[name] = pipeline


def process_request(pipeline, request):
    start_time = time.time()

    result = pipeline.run(**request)

    end_time = time.time()
    info = {
        "request": request,
        "response": result,
        "time": f"{(end_time - start_time):.2f}",
    }
    try:
        logger.info(json.dumps(info))
    except Exception:
        pass

    return result


def make_pipeline(pipeline_config, yaml_conf):
    definitions = {}  # definitions of each component from the YAML.
    component_definitions = copy.deepcopy(yaml_conf.get("components", []))

    for definition in component_definitions:
        Pipeline._overwrite_with_env_variables(definition)
        name = definition.pop("name")
        definitions[name] = definition

    pipeline = Pipeline()

    components: dict = {}  # instances of component objects.
    for node_config in pipeline_config["nodes"]:
        name = node_config["name"]
        component = Pipeline._load_or_get_component(
            name=name, definitions=definitions, components=components)
        pipeline.add_node(
            component=component, name=node_config["name"],
            inputs=node_config.get("inputs", []))

    return pipeline


class PipelineModel(object):
    pipeline = None
    pipeline_name = None

    def __init__(self, pipeline=None):
        pipeline_config, yaml_conf = PIPELINES[pipeline or self.pipeline_name]
        self.pipeline = make_pipeline(pipeline_config, yaml_conf)

        self.pipeline_config = pipeline_config
        self.yaml_config = yaml_conf

        logger.info(
            f"Loaded pipeline nodes: {self.pipeline.graph.nodes.keys()}")

    def _pre_process(self, payload):
        return payload.dict()

    def _post_process(self, prediction):
        return prediction

    def _predict(self, payload):
        return process_request(self.pipeline, payload)

    def predict(self, payload):
        if payload is None:
            raise ValueError(NO_VALID_PAYLOAD.format(payload))

        pre_processed_payload = self._pre_process(payload)

        prediction = self._predict(pre_processed_payload)

        logger.info(prediction)
        post_processed_result = self._post_process(prediction)

        return post_processed_result
