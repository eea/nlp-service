from .api import SimilarityRequest


def runtimetest(app):
    payload = SimilarityRequest()
    res = app.state.similarity_model.predict(payload)
    assert res
