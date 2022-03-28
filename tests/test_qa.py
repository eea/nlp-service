import requests

payload_query = {
    "query": "What is GHG",
    "params": {
        "use_dp": False,
        "custom_query": {},
        "RawRetriever": {},
        "DensePassageRetriever": {},
        "AnswerExtraction": {},
    },
}


payload_dp_query = {
    "query": "What is GHG",
    "params": {
        "use_dp": True,
        "custom_query": {},
        "RawRetriever": {},
        "DensePassageRetriever": {},
        "AnswerExtraction": {},
    },
}


def test_qa(api_server):
    url = f"{api_server}/query"
    resp = requests.post(url, json=payload_query)
    data = resp.json()

    assert len(data["answers"]) > 0
    assert data["answers"][0]["answer"]
