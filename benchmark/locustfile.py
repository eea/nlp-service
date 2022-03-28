from locust import HttpUser, task, run_single_user

import json

URL = "/_es/globalsearch/_search"

with open("./qa.json") as f:
    qa_body = json.load(f)

with open("./fulltext.json") as f:
    fulltext_body = json.load(f)

with open("./similarity.json") as f:
    similarity_body = json.load(f)

agg_bodies = []
for i in range(1, 11):
    fname = f"agg-{i}.json"
    with open(fname) as f:
        agg_bodies.append(json.load(f))


class QAUser(HttpUser):
    host = "http://localhost:3000"

    @task(1)
    def get_fulltext(self):
        with self.client.get(URL, json=fulltext_body, catch_response=True) as response:
            try:
                r = response.json()
                hits = r["hits"]["hits"]
                if len(hits) != 10:
                    response.failure("Did not get 10 answers back")
            except json.JSONDecodeError:
                response.failure("Response could not be decoded as JSON")
            except KeyError:
                response.failure("No hits")

    @task(2)
    def get_answer(self):
        with self.client.get(URL, json=qa_body, catch_response=True) as response:
            try:
                r = response.json()
                answers = r["answers"]
                if len(answers) != 10:
                    response.failure("Did not get 10 answers back")
            except json.JSONDecodeError:
                response.failure("Response could not be decoded as JSON")
            except KeyError:
                response.failure("No answers")

    @task(3)
    def get_similarity(self):
        with self.client.get(
            URL, json=similarity_body, catch_response=True
        ) as response:
            try:
                r = response.json()
                clusters = r["clusters"]
                if len(clusters) == 0:
                    response.failure("Did not get similarity clusters back")
            except json.JSONDecodeError:
                response.failure("Response could not be decoded as JSON")
            except KeyError:
                response.failure("No clusters")

    @task(4)
    def get_aggregations(self):
        for body in agg_bodies:
            with self.client.get(URL, json=body, catch_response=True) as response:
                try:
                    r = response.json()
                    aggs = r["aggregations"]
                    if len(aggs) == 0:
                        response.failure("Did not get aggregations back")
                except json.JSONDecodeError:
                    response.failure("Response could not be decoded as JSON")
                except KeyError:
                    response.failure("No aggregations")


if __name__ == "__main__":
    run_single_user(QAUser)
