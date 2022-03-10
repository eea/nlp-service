import os

import pytest


@pytest.fixture(scope="session")
def api_server():
    return os.environ.get("NLPSERVICE", "http://localhost:8000/api")
