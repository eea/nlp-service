import os
import urllib.request
from pathlib import Path

from app.core.model import register_model
from app.core.pipeline import PipelineModel  # , process_request


@register_model("tika_model")
class TikaModel(PipelineModel):
    pipeline_name = "converter"

    def _pre_process(self, payload):
        url = payload.url
        try:
            fpath, status = urllib.request.urlretrieve(url)
        except Exception:
            raise

        return {"params": {"Tika": {"file_paths": [Path(fpath)], "meta": {"id": url}}}}

    def _post_process(self, payload):
        for fpath in payload["params"]["Tika"]["file_paths"]:
            os.unlink(fpath.as_posix())

        doc_id = payload["params"]["Tika"]["meta"]["id"]

        payload["documents"] = [
            {"id": doc_id, "text": doc.content, "meta": doc.meta}
            for doc in payload["documents"]
        ]

        return payload
