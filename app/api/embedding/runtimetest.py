from .api import EmbeddingRequest


def runtimetest(app):
    payload = EmbeddingRequest()
    res = app.state.services['embedding'].predict(payload)
    assert res
