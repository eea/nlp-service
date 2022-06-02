from app.core.model import register_model
from app.core.pipeline import ComponentModel


@register_model("querysearch")
class QuerySearch(ComponentModel):
    component_name = "QuerySearch"
