from app.core.components import LangDetect
from app.core.model import register_model


@register_model("langdetect_model")
class LangDetectModel(LangDetect):
    component_name = "LangDetect"
