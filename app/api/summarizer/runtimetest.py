from .api import SummaryRequest


def runtimetest(app):
    payload = SummaryRequest()
    res = app.state.summarizer_model.predict(payload)
    assert res
