from .api import NERRequest


def runtimetest(app):
    payload = NERRequest()
    res = app.state.ner_model.predict(payload)
    assert res
