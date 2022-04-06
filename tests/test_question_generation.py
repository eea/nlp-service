import requests

payload = {
    "num_questions": 3,
    "text": """With 77 % of European external trade and 35 % of all trade by value between
  EU Member States moved by sea, maritime transport is a key part of the international
  supply chain. Despite a drop in shipping activity in 2020 due to the effects of the
  COVID-19 pandemic, the sector is expected to grow strongly over the coming decades,
  fueled by rising demand for primary resources and container shipping.\n\nAgainst this
  background, the European Maritime Transport Environmental Report, launched today by the
  European Environment Agency and the European Maritime Safety Agency, marks the first
  comprehensive health-check of the sector. The report shows that ships produce 13.5 % of
  all greenhouse gas emissions from transport in the EU, behind emissions from road
  transport (71 %) and aviation (14.4 %). Sulphur dioxide (SO2) emissions from ships
  calling in European ports amounted to approximately 1.63 million tonnes in 2019,
  a figure which is expected to fall further over the coming decades due to stricter
  environmental rules and measures.""",
}


def test_question_generation(api_server):
    url = f"{api_server}/questiongeneration"
    resp = requests.post(url, json=payload)
    data = resp.json()

    assert data["text"]

    questions = data["questions"]

    assert len(questions) == 3

    for q in questions:
        assert q["question"]
        assert q["answer"]
