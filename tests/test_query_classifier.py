import requests


class TestQueryClassifier:
    def test_query_classifier_interrogative(self, api_server):
        url = f"{api_server}/query-classifier"
        resp = requests.post(url, json={"query": "Where to go on holiday"})
        data = resp.json()
        assert data["answer"] == "query:interrogative"

    def test_query_classifier_keyword(self, api_server):
        url = f"{api_server}/query-classifier"
        resp = requests.post(url, json={"query": "water quality"})
        data = resp.json()
        assert data["answer"] == "query:keyword"

    def test_query_classifier_statement(self, api_server):
        url = f"{api_server}/query-classifier"
        resp = requests.post(url, json={"query": "water is good"})
        data = resp.json()
        assert data["answer"] == "query:declarative"
