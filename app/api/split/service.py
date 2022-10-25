import os
import urllib.request
from pathlib import Path

from app.core.model import register_model
from app.core.pipeline import PipelineModel, process_request


@register_model("split_model")
class SplitModel(PipelineModel):
    pipeline_name = "split"


    def _predict(self, payload):
        processed = process_request(
            self.pipeline, {"params": {"Split": {"payload": payload}}}
        )

        return processed

