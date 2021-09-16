from app.core.model import register_model
from app.core.pipeline import PipelineModel

# @register_model("question_generation_model_a")
# class QuestionGenerationModelA(PipelineModel):
#     def __init__(self):
#         from .lib.questiongeneration_pipeline import pipeline
#         self.pipeline = pipeline('multitask-qa-qg')     # question-generation
#
#     def predict(self, payload):
#         # , num_questions=payload.num_questions
#         import pdb
#         pdb.set_trace()
#         prediction = self.pipeline(payload.text)
#
#         return prediction


@register_model("question_generation_model_b")
class QuestionGenerationModelB(PipelineModel):
    def __init__(self):
        from .lib.questiongeneration import QuestionGenerator
        self.pipeline = QuestionGenerator()

    def predict(self, payload):
        prediction = self.pipeline.generate(
            payload.text,
            num_questions=payload.num_questions)

        return {"text": payload.text, "questions": prediction}
