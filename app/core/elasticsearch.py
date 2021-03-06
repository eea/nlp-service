""" Utilities to deal with ES queries
"""

import jq

QUERY_SIMPLE_MATCH = jq.compile(".match.text")
QUERY_MATCH_ALL = jq.compile(".function_score.query.bool.must[].match_all")
QUERY_MATCH_TEXT = jq.compile(".function_score.query.bool.must[].multi_match.query")
QUERY_QUERY = jq.compile(".query")


def get_search_term(body):
    """Extract the text search term from an ES query"""
    if isinstance(body, str):
        return body

    strategies = [QUERY_MATCH_TEXT, QUERY_MATCH_ALL, QUERY_SIMPLE_MATCH, QUERY_QUERY]
    search_term = ""

    for compiled in strategies:
        try:
            search_term = compiled.input(body).first()
        except Exception as e:
            print(e)
        if search_term:
            break

    if not isinstance(search_term, str):
        print("Extracted search term not a text: ", search_term)
        return ""

    return search_term


def get_body_from(payload):
    start = payload.get("from", payload.get("from_"))

    if start is None:
        return 0

    return start
