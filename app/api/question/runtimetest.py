from .api import QuestionRequest


def runtimetest(app):
    payload = QuestionRequest()
    res = app.state.QUESTION_CLASSIFIER.predict(payload)
    assert res
