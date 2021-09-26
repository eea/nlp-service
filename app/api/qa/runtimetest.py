from .api import QA_Request


def runtimetest(app):
    payload = QA_Request()
    res = app.state.dp_qa.predict(payload)
    assert res
