import copy
import json
import time
from base64 import b64encode
from typing import Dict, Optional

from app.core.messages import NO_VALID_PAYLOAD
from haystack.pipelines.base import Pipeline as BasePipeline
from haystack.pipelines.config import (get_component_definitions,
                                       get_pipeline_definition)
from loguru import logger
from networkx.drawing.nx_agraph import to_agraph

PIPELINES = {}
COMPONENTS = {}


def add_pipeline(name, pipeline):
    PIPELINES[name] = pipeline


# def add_components(components):
#     for component in components:
#         name = component["name"]
#         COMPONENTS[name] = component


def load_components(config, components):
    """Instantiate components based on a configuration"""

    from haystack.nodes.base import BaseComponent

    for definition in config.get("components", []):
        copied = copy.deepcopy(definition)
        name = copied.pop("name")
        params = copied.get("params", {})

        # loads references to other components
        for k, v in params.items():
            if isinstance(v, str) and v in components:
                params[k] = components[v]

        try:
            components[name] = BaseComponent.load_from_args(copied["type"], **params)
        except Exception:
            print(f"Error loading: (${copied['type']}) with params: ${params}")
            raise


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
        logger.debug(json.dumps(info))
    except Exception:
        pass

    return result


class Pipeline(BasePipeline):
    """A variant of Pipeline that does not call validate_config.

    Based on haystack.pipelines.base.Pipeline.load_from_config
    """

    @classmethod
    def load_from_config(
        cls,
        pipeline_config: Dict,
        pipeline_name: Optional[str] = None,
        overwrite_with_env_variables: bool = True,
    ):
        pipeline_definition = get_pipeline_definition(
            pipeline_config=pipeline_config, pipeline_name=pipeline_name
        )
        component_definitions = get_component_definitions(
            pipeline_config=pipeline_config,
            overwrite_with_env_variables=overwrite_with_env_variables,
        )

        pipeline = cls()

        components: dict = {}  # instances of component objects.
        for node in pipeline_definition["nodes"]:
            name = node["name"]
            component = cls._load_or_get_component(
                name=name, definitions=component_definitions, components=components
            )
            pipeline.add_node(
                component=component, name=name, inputs=node.get("inputs", [])
            )

        return pipeline


def make_pipeline(pipeline_config, service_conf):
    components = service_conf.get("components", [])

    conf = dict(components=components, pipelines=[pipeline_config])

    pipeline = Pipeline.load_from_config(conf, overwrite_with_env_variables=True)

    return pipeline


class PipelineModel(object):
    """A component that can be instantiated as a singleton model.

    It uses a declared Pipeline to process (and identifies is based on name)
    """

    pipeline = None
    pipeline_name = None

    def __init__(self, pipeline=None):
        pipeline_config, yaml_conf = PIPELINES[pipeline or self.pipeline_name]
        self.pipeline = make_pipeline(pipeline_config, yaml_conf)

        self.pipeline_config = pipeline_config
        self.yaml_config = yaml_conf

        logger.info(f"Loaded pipeline nodes: {self.pipeline.graph.nodes.keys()}")

    def _pre_process(self, payload):
        return payload.dict()

    def _post_process(self, prediction):
        return prediction

    def _predict(self, payload):
        return process_request(self.pipeline, payload)  # {"meta": payload}

    def predict(self, payload):
        if payload is None:
            raise ValueError(NO_VALID_PAYLOAD.format(payload))

        pre_processed_payload = self._pre_process(payload)

        prediction = self._predict(pre_processed_payload)

        # logger.info(prediction)
        post_processed_result = self._post_process(prediction)

        return post_processed_result

    def graph_pipeline(self):

        try:
            import pygraphviz

            pygraphviz
        except ImportError:
            raise ImportError(
                "Could not import `pygraphviz`. Please install via: \n"
                "pip install pygraphviz\n"
                "(You might need to run this first: "
                "apt install libgraphviz-dev graphviz )"
            )

        graphviz = to_agraph(self.pipeline.graph)
        graphviz.layout("dot")
        bits = graphviz.draw(path=None, format="svg")

        encoded = b64encode(bits)

        return encoded


class ComponentModel(object):
    component_name = None

    def __init__(self, component=None, pipeline=None):
        component = component or self.component_name
        component_config = COMPONENTS[component]

        conf = dict(components=[component_config], pipelines=[])

        component_definitions = get_component_definitions(
            pipeline_config=conf,
            overwrite_with_env_variables=True,
        )
        components = {}
        for name in component_definitions:
            c = BasePipeline._load_or_get_component(
                name=name, definitions=component_definitions, components=components
            )
            components[name] = c

        self.component = components[component]
        logger.info("Initialized component:", self.component)
