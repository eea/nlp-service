import requests

payload = {
    "base": "eight accidental medium to large oil tanker spills out of a worldwide total of 62 occurred in EU waters over the past decade",
    "candidates": [
        "underwater noise levels in EU waters have more than doubled between 2014 and 2019",
        "maritime transport can keep growing and delivering on our citizens’ daily needs, in harmony with the environment",
        "out of a total of 18 large accidental oil spills in the word since 2010, only three were located in the EU (17%)",
    ],
}


def test_similarity(api_server):
    url = f"{api_server}/similarity"
    resp = requests.post(url, json=payload)
    data = resp.json()

    assert data["base"] == payload["base"]
    assert len(data["predictions"]) == 3

    predictions = sorted(data["predictions"], key=lambda p: p["score"], reverse=True)
    assert (
        predictions[0]["text"]
        == "out of a total of 18 large accidental oil spills in the word since 2010, only three were located in the EU (17%)"
    )
