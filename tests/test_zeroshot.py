import requests

payload = {
    "text": "EU maritime transport faces a crucial decade to transition to a more economically, socially and environmentally sustainable sector. Already, most ships calling in the EU have reduced their speed by up to 20 % compared to 2008, thereby also reducing emissions, according to the report.",
    "candidate_labels": [
        "Air pollution",
        "Climate change",
        "Biodiversity",
        "Land use",
        "Water and marine environment",
        "Transport",
        "Industry",
        "Energy",
        "Agriculture",
    ],
}


def test_similarity(api_server):
    url = f"{api_server}/zeroshot"
    resp = requests.post(url, json=payload)
    data = resp.json()

    predictions = sorted(data["labels"], key=lambda p: p["score"], reverse=True)

    assert [p["label"] for p in predictions] == [
        "Transport",
        "Water and marine environment",
    ]
