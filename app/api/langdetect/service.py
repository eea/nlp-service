from app.core.model import register_model

from langdetect import DetectorFactory, detect, detect_langs

DetectorFactory.seed = 0


@register_model("langdetect_model")
class LangDetectModel(object):
    def predict(self, payload):
        meth = payload.options.debug and detect_langs or detect
        return {"predictions": [meth(text) for text in payload.texts]}
