from app.core.model import register_model
from app.core.pipeline import PipelineModel     # , process_request
import urllib.request
from pathlib import Path
import os


@register_model("tika_model")
class TikaModel(PipelineModel):
    pipeline_name = "converter"

    def _pre_process(self, payload):
        url = payload.url
        try:
            fpath, status = urllib.request.urlretrieve(url)
        except Exception:
            raise

        return {
            "params": {
                "Tika": {
                    "file_paths": [Path(fpath)],
                }
            }
        }

    def _post_process(self, payload):
        for fpath in payload['params']['Tika']['file_paths']:
            os.unlink(fpath.as_posix())
        return payload
