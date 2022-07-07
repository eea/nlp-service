import json
import os

import pytest

from app.core.components.searchlib.highlight import Highlight


@pytest.fixture
def sample():
    sample_name = os.path.join(os.path.dirname(__file__) + "/fixtures/highlight_algorithm", "sample.txt")
    with open(sample_name) as f:
        return json.load(f)


@pytest.fixture
def sample2():
    sample_name = os.path.join(os.path.dirname(__file__) + "/fixtures/highlight_algorithm", "sample2.txt")
    with open(sample_name) as f:
        return json.load(f)


@pytest.fixture
def highlight():
    search_term = "transportation in agriculture"
    return Highlight(search_term=search_term)


@pytest.fixture
def highlight2():
    search_term = "transport in the agriculture with a lot of emissions in the air from transport"
    return Highlight(search_term=search_term)


@pytest.fixture
def empty_highlight():
    return Highlight(search_term="")


def test_language(highlight, empty_highlight):
    assert highlight.language == "en"
    assert empty_highlight.language == []


def test_detect_language():
    finnish = Highlight(search_term="tämä on ranskankielinen tekstinäyte")
    assert finnish.language == "fi"

    french = Highlight(search_term="ceci est un exemple de texte en français")
    assert french.language == "fr"

    greek = Highlight(search_term="αυτό είναι ένα δείγμα γαλλικού κειμένου")
    assert greek.language == "el"

    spanish = Highlight(search_term="esta es una muestra de texto en francés")
    assert spanish.language == "es"


def test_stop_words(highlight, empty_highlight):
    # given
    assert highlight.language == "en"
    # when
    stop_words = highlight.stop_words
    # then
    assert "the" in stop_words
    assert any(item in ["the", "this", "a", "an", "that"] for item in stop_words)

    assert "the" not in empty_highlight.stop_words
    assert empty_highlight.stop_words == []


def test_create_positions(highlight, empty_highlight):
    assert empty_highlight._create_positions() == {}

    # given the search_term "transportation in agriculture" from fixture
    tokens_position = highlight._create_positions()

    assert tokens_position["transportation"] == {0}
    assert tokens_position["in"] == {1}
    assert tokens_position["agriculture"] == {2}


def test_is_consecutive_tokens(highlight):
    set1 = {1, 2, 4}
    set2 = {7}
    set3 = {3}

    res1 = highlight._is_consecutive_tokens(set1, set2)
    res2 = highlight._is_consecutive_tokens(set1, set3)

    assert res1 is False
    assert res2 is True


def test_is_highlighted(highlight):
    # given
    token1 = "agriculture"
    token2 = "<em> the </em>"
    token3 = ""
    token4 = None

    # when
    res1 = highlight._is_highlighted(token1)
    res2 = highlight._is_highlighted(token2)
    res3 = highlight._is_highlighted(token3)
    res4 = highlight._is_highlighted(token4)

    # then
    assert res1 is False
    assert res2 is True
    assert res3 is False
    assert res4 is False


def test_get_highlighted(highlight):
    highlighted_token1 = "<em>token1</em>"
    highlighted_token2 = "<em>token2</em>"

    res1 = highlight._get_highlighted(highlighted_token1)
    res2 = highlight._get_highlighted(highlighted_token2)

    assert res1 == "token1"
    assert res2 == "token2"


def test_adjust(highlight, sample, highlight2, sample2):
    assert "<em>in</em>" in json.dumps(sample)
    assert "<em>agriculture</em> <em>in</em>" in json.dumps(sample)
    clean_text = highlight.adjust(sample)
    assert "<em>in</em>" not in json.dumps(clean_text)
    assert "<em>agriculture</em> <em>in</em>" not in json.dumps(clean_text)

    assert "<em>agriculture</em> <em>with</em> <em>the</em>" in json.dumps(sample2)
    clean_text = highlight2.adjust(sample2)
    assert "<em>agriculture</em> <em>with</em> <em>the</em>" not in json.dumps(clean_text)
    assert "<em>agriculture</em> <em>with</em> <em>a</em>" in json.dumps(clean_text)
