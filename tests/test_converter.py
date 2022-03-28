import requests

payload = {
    "url": "https://www.eea.europa.eu/api/SITE/publications/exploring-the-social-challenges-of/at_download/file"
}


def test_converter(api_server):
    url = f"{api_server}/converter"
    resp = requests.post(url, json=payload)
    data = resp.json()

    assert len(data["documents"]) == 1
    assert len((data["documents"][0])["text"]) > 0
