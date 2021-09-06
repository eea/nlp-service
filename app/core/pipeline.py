import json
import time
from pathlib import Path

from app.core.config import PIPELINE_YAML_PATH
from app.core.messages import NO_VALID_PAYLOAD
from haystack import Pipeline
from loguru import logger


def _process_request(pipeline, request):
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


class PipelineModel(object):
    pipeline = None
    pipeline_name = None

    def __init__(self):
        self.pipeline = Pipeline.load_from_yaml(
            Path(PIPELINE_YAML_PATH), pipeline_name=self.pipeline_name
        )
        logger.info(
            f"Loaded pipeline nodes: {self.pipeline.graph.nodes.keys()}")

    def _pre_process(self, payload):
        return payload.dict()

    def _post_process(self, prediction):
        return prediction

    def _predict(self, payload):
        return _process_request(self.pipeline, payload)

    def predict(self, payload):
        if payload is None:
            raise ValueError(NO_VALID_PAYLOAD.format(payload))

        pre_processed_payload = self._pre_process(payload)
        prediction = self._predict(pre_processed_payload)
        logger.info(prediction)
        post_processed_result = self._post_process(prediction)

        return post_processed_result
