from typing import Optional

from haystack.nodes.base import BaseComponent
from langdetect import DetectorFactory, detect, detect_langs
from app.core.elasticsearch import get_search_term, get_body_from

DetectorFactory.seed = 0


class LangDetect(BaseComponent):
    outgoing_edges = 1

    def run(self, params: Optional[dict] = None, ):
        print(params)
        payload = params["payload"]

        search_term = get_search_term(payload["query"])
        search_term = self._preprocess(search_term)

        detected_language = self.predict(search_term)
        payload["detected_language"] = detected_language

        return payload, "output_1"

    def predict(self, payload):

        if not isinstance(payload, dict):
            payload = payload.dict()

        meth = payload["options"]["debug"] and detect_langs or detect
        return {"predictions": [meth(text) for text in payload["texts"]]}

    def _preprocess(self, search_term, debug=False):
        return {
            "texts": [search_term],
            "options": {
                "debug": debug
            }
        }
