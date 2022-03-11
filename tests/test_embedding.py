import requests

payload = {
    "is_passage": False,
    "snippets": [
        "Maritime transport plays and will continue to play an essential role in global and European trade and economy.",
        "The European Environment Agency provides sound, independent information on the environment for those involved in developing, adopting, implementing and evaluating environmental policy, and also the general public.",
        "Climate-friendly practices for sourcing raw materials hold significant potential to cut greenhouse gas emissions in Europe and globally.",
    ],
}


def test_embedding_no_passage(api_server):
    url = f"{api_server}/embedding"
    resp = requests.post(url, json=payload)
    data = resp.json()

    assert len(data["embeddings"]) == 3

    for i in range(len(data["embeddings"])):
        assert data["embeddings"][i]["text"]
        assert data["embeddings"][i]["embedding"]


def test_embedding_is_passage(api_server):
    url = f"{api_server}/embedding"
    dump = dict(is_passage=True, snippets=payload["snippets"])
    resp = requests.post(url, json=dump)
    data = resp.json()

    assert len(data["embeddings"]) == 3

    for i in range(len(data["embeddings"])):
        assert data["embeddings"][i]["text"]
        assert data["embeddings"][i]["embedding"]
