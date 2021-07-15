import json
import time
from pathlib import Path

from app.core.config import PIPELINE_YAML_PATH, QUERY_PIPELINE_NAME
from app.core.messages import NO_VALID_PAYLOAD
from app.core.model import register_model
from app.data_models.qa import QA_Request, Response
from haystack import Pipeline
from loguru import logger


def _process_request(pipeline, request):
    start_time = time.time()

    filters = {}
    if request.filters:
        # put filter values into a list and remove filters with null value
        for key, values in request.filters.items():
            if values is None:
                continue
            if not isinstance(values, list):
                values = [values]
            filters[key] = values

    result = pipeline.run(
        query=request.query,
        filters=filters,
        top_k_retriever=request.top_k_retriever,
        top_k_reader=request.top_k_reader,
    )

    end_time = time.time()
    info = {
        "request": request.dict(),
        "response": result,
        "time": f"{(end_time - start_time):.2f}",
    }
    logger.info(json.dumps(info))

    return result


@register_model("qa")
class QAModel(object):
    pipeline = None

    def __init__(self):
        self.pipeline = Pipeline.load_from_yaml(
            Path(PIPELINE_YAML_PATH), pipeline_name=QUERY_PIPELINE_NAME
        )
        logger.info(
            f"Loaded pipeline nodes: {self.pipeline.graph.nodes.keys()}")

    def _pre_process(self, payload):
        return payload

    def _post_process(self, prediction):
        return prediction

    def _predict(self, payload):
        return _process_request(self.pipeline, payload)

    def predict(self, payload: QA_Request) -> Response:
        if payload is None:
            raise ValueError(NO_VALID_PAYLOAD.format(payload))

        pre_processed_payload = self._pre_process(payload)
        prediction = self._predict(pre_processed_payload)
        logger.info(prediction)
        post_processed_result = self._post_process(prediction)

        return post_processed_result


# RESULT_UNIT_FACTOR = 100000
# def _load_local_model(self):
#     self.model = joblib.load(self.path)
# def _pre_process(self, payload: HousePredictionPayload) -> List:
#     logger.debug("Pre-processing payload.")
#     result = np.asarray(payload_to_list(payload)).reshape(1, -1)
#     return result
# def _post_process(self, prediction: np.ndarray) -> HousePredictionResult:
#     logger.debug("Post-processing prediction.")
#     result = prediction.tolist()
#     human_readable_unit = result[0] * self.RESULT_UNIT_FACTOR
#     hpp = HousePredictionResult(median_house_value=human_readable_unit)
#     return hpp
# def _predict(self, features: List) -> np.ndarray:
#     logger.debug("Predicting.")
#     prediction_result = self.model.predict(features)
#     return prediction_result
# from typing import List
# import joblib
# import numpy as np
# from app.data_models.payload import HousePredictionPayload, payload_to_list
# from app.data_models.prediction import HousePredictionResult
