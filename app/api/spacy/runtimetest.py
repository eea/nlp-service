from .api import SpacyNERRequest


def runtimetest(app):
    payload = SpacyNERRequest()
    res = app.state.spacy_ner_model.predict(payload)
    assert res
