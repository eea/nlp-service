from app.core.config import QUERY_PIPELINE_NAME
from app.core.model import register_model
from app.core.pipeline import Pipeline
from app.data_models.qa import QA_Request, Response


@register_model("qa")
class QAModel(Pipeline):
    pipeline_name = QUERY_PIPELINE_NAME

    def predict(self, payload: QA_Request) -> Response:
        return super(QAModel, self).predict(payload)

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
