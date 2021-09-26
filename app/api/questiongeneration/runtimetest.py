from .api import QuestionGenerationRequest


def runtimetest(app):
    payload = QuestionGenerationRequest()
    res = app.state.question_generation_model_b.predict(payload)
    assert res
