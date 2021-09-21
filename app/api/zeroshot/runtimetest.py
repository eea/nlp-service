from .api import ZeroShotRequest


def runtimetest(app):
    payload = ZeroShotRequest()
    res = app.state.zeroshot_classifier_model.predict(payload)
    assert res
