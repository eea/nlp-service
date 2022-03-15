import requests

payload = {
    "query": {
        "function_score": {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": "Where can I access greenhouse gas data?",
                                "minimum_should_match": "75%",
                                "fields": [
                                    "title^2",
                                    "subject^1.5",
                                    "description^1.5",
                                    "all_fields_for_freetext",
                                ],
                            }
                        }
                    ],
                    "filter": [
                        {
                            "constant_score": {
                                "filter": {
                                    "bool": {
                                        "should": [
                                            {
                                                "bool": {
                                                    "must_not": {
                                                        "exists": {"field": "expires"}
                                                    }
                                                }
                                            },
                                            {
                                                "range": {
                                                    "expires": {
                                                        "gte": "2022-03-15T11:42:33Z"
                                                    }
                                                }
                                            },
                                        ]
                                    }
                                }
                            }
                        },
                        {
                            "bool": {
                                "should": [{"range": {"readingTime": {}}}],
                                "minimum_should_match": 1,
                            }
                        },
                        {
                            "bool": {
                                "should": [{"range": {"issued.date": {}}}],
                                "minimum_should_match": 1,
                            }
                        },
                        {
                            "bool": {
                                "should": [{"term": {"language": "en"}}],
                                "minimum_should_match": 1,
                            }
                        },
                        {"term": {"hasWorkflowState": "published"}},
                        {
                            "constant_score": {
                                "filter": {
                                    "range": {
                                        "issued.date": {"lte": "2022-03-15T11:42:38Z"}
                                    }
                                }
                            }
                        },
                    ],
                }
            },
            "functions": [
                {"exp": {"issued.date": {"offset": "30d", "scale": "1800d"}}}
            ],
            "score_mode": "sum",
        }
    },
    "highlight": {
        "fragment_size": 200,
        "number_of_fragments": 3,
        "fields": {
            "description.highlight": {
                "highlight_query": {
                    "bool": {
                        "must": [
                            {
                                "match": {
                                    "description.highlight": {
                                        "query": "Where can I access greenhouse gas data?"
                                    }
                                }
                            }
                        ],
                        "should": [
                            {
                                "match_phrase": {
                                    "description.highlight": {
                                        "query": "Where can I access greenhouse gas data?",
                                        "slop": 1,
                                        "boost": 10,
                                    }
                                }
                            }
                        ],
                    }
                }
            }
        },
    },
    "aggs": {},
    "size": 10,
    "runtime_mappings": {
        "op_cluster": {
            "type": "keyword",
            "script": {
                "source": 'emit("_all_"); def clusters_settings = [["name": "News", "values": ["News","Article"]],["name": "Publications", "values": ["Report","Indicator","Briefing","Topic page","Country fact sheet"]],["name": "Maps and charts", "values": ["Figure (chart/map)","Chart (interactive)","Infographic","Dashboard","Map (interactive)"]],["name": "Data", "values": ["External data reference","Data set"]],["name": "Others", "values": ["Webpage","Organisation","FAQ","Video","Contract opportunity","Glossary term","Collection","File","Adaptation option","Guidance","Research and knowledge project","Information portal","Tool","Case study"]]]; def vals = doc[\'objectProvides\']; def clusters = [\'All\']; for (val in vals) { for (cs in clusters_settings) { if (cs.values.contains(val)) { emit(cs.name) } } }'
            },
        }
    },
    "params": {},
    "source": {"exclude": ["fulltext"]},
    "track_total_hits": True,
}


def test_search(api_server):
    url = f"{api_server}/_search"
    resp = requests.post(url, json=payload)
    data = resp.json()
    assert len(data["hits"]["hits"]) > 0

    doc = data["hits"]["hits"][0]

    assert doc["_id"]
    assert doc["_source"]
    assert doc["highlight"]
