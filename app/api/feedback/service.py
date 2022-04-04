from app.core.model import register_model
from app.core.pipeline import ComponentModel


@register_model("feedback_document_store")
class FeedbackDocumentStore(ComponentModel):
    component_name = "FeedbackModel"
    pipeline_name = "feedback"
