import requests

payload = {
    "texts": [
        "EEA Executive Director Hans Bruyninckx welcomed President Čaputová and her delegation, which also included Andrej Doležal, Slovakia’s Minister of Transport and Construction. The Executive Director thanked the President for Slovakia’s strong commitment to the EU’s environmental goals and explained how the EEA is working to provide reliable data and information to policymakers - specifically in supporting the European Green Deal and accompanying legislation, which aims to shift Europe towards a sustainable, low-carbon future."
    ]
}


def test_ner(api_server):
    url = f"{api_server}/ner"
    resp = requests.post(url, json=payload)
    data = resp.json()
    entities = data["entities"]

    assert len(entities) == 1
    extracted = entities[0]

    assert extracted[0]["word"] == "E"
    assert extracted[1]["word"] == "EA"
    assert extracted[1]["entity"] == "B-ORG"
