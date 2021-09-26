from .api import EmbeddingRequest


def runtimetest(app):
    payload = EmbeddingRequest()
    res = app.state.embedding_model.predict(payload)
    assert res
