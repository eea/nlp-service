from .api import TikaRequest


def runtimetest(app):
    payload = TikaRequest()
    res = app.state.tika_model.predict(payload)
    assert res
