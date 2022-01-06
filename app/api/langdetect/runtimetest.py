from .api import LangDetectRequest


def runtimetest(app):
    payload = LangDetectRequest()
    res = app.state.langdetect_model.predict(payload)
    assert res
