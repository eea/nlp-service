import re

import nltk

try:
    from nltk.corpus import stopwords
except ImportError:
    nltk.download("stopwords")
finally:
    from nltk.corpus import stopwords

lang_code_mapping = {
    "bg": "bulgarian",
    "cs": "czech",
    "de": "german",
    "el": "greek",
    "en": "english",
    "es": "spanish",
    "et": "estonian",
    "fr": "french",
    "hr": "croatian",
    "it": "italian",
    "lt": "lithuanian",
    "mt": "maltese",
    "nl": "dutch",
    "pl": "polish",
    "pt": "portuguese",
    "ro": "romanian",
    "sk": "slovak",
    "sl": "slovenian",
    "sv": "swedish",
    "tr": "turkish",
}


def get_stop_words(language_code):
    stop_words = []

    if language_code:
        language = lang_code_mapping[language_code]
        stop_words = stopwords.words(language)
    else:
        # default language is 'english'
        stop_words = stopwords.words("english")

    return stop_words


def create_positions_dict(text):
    tokens_position = {}

    if text is None:
        return tokens_position

    # remove delimiters
    delimiters = ",.!?/&-:; "
    splitter = "[" + "\\".join(delimiters) + "]"
    new_text = " ".join(w for w in re.split(splitter, text.lower()) if w)

    # get the tokens
    tokens = new_text.split()

    curr_position = 0

    while curr_position < len(tokens):
        if tokens[curr_position] not in tokens_position:
            tokens_position[tokens[curr_position]] = set()

        tokens_position[tokens[curr_position]].add(curr_position)

        curr_position = curr_position + 1

    return tokens_position


def test_consecutive_tokens(set1, set2):
    for elem1 in set1:
        if (elem1 + 1) in set2:
            return True

    return False


def test_highlighting(text):
    if ("<em>" in text) and ("</em>" in text):
        return True

    return False


def get_highlighted_text(text):
    text = text.replace("<em>", "")
    text = text.replace("</em>", "")

    return text


def get_sequences(searched_text, original_es_highlight, stop_words):
    """
    store a list of tuples (start_seq, end_seq, status) in highlighted_sequences
    a tuple represent the start and the end of a highlighted sequence and if the sequence
    has only stop words ('r' - from remove) or not ('k' - keep)

    Algorithm used in get_sequences(searched_text, original_es_highlight):
    Go through each word from original_es_highlight, one by one.
    At every step, we need to know which is the beginning of the subsequence of tokens from original_es_highlight,
    that are consecutive in searched_text, that is ending in the current token from original_es_highlight.
    In order to do so, we hold in a variable the index of the token that is at the beginning of this subsequence.
    When we advance to a new token from original_es_highlight,
    we need first to check if the token can continue the already found sequence until the current moment
    meaning if the current token is marked (with <em> , </em>) and if it is successive in the searched_text.
    if the current token is marked and is consecutive to the previous token
    (we determine that by looking at the precedence of tokens in searched_text),
    then we just go on to the next token, the beginning of the sequence remains the same.
    if not (the token is not highlighted because is not part of searched_text, or, if it is, is not successive to the precedent token),
    then it means that the current subsequence ends at the previous token (including the previous token).
    in the process we also verify each token from the sequences
    so that we know if a sequence contains only stop words or not.
    """

    highlighted_sequences = []

    if (searched_text is None) or (original_es_highlight is None):
        return highlighted_sequences

    searched_tokens_positions = create_positions_dict(searched_text)

    highlighted_tokens = original_es_highlight.split()

    curr_position = 0

    start_seq = 0
    end_seq = 0
    only_stop_words_in_seq = True

    while curr_position < len(highlighted_tokens):
        curr_token = highlighted_tokens[curr_position]

        if test_highlighting(curr_token):
            dehighlighted_curr_token = get_highlighted_text(curr_token)

            if dehighlighted_curr_token.lower() not in stop_words:
                only_stop_words_in_seq = False

            if curr_position == 0:
                curr_position = curr_position + 1
            else:
                prev_token = highlighted_tokens[curr_position - 1]

                if test_highlighting(prev_token):
                    dehighlighted_prev_token = get_highlighted_text(prev_token)
                    if (dehighlighted_curr_token in searched_tokens_positions) and (
                        dehighlighted_prev_token in searched_tokens_positions
                    ):

                        curr_token_set = searched_tokens_positions[
                            dehighlighted_curr_token.lower()
                        ]
                        prev_token_set = searched_tokens_positions[
                            dehighlighted_prev_token.lower()
                        ]

                        if test_consecutive_tokens(prev_token_set, curr_token_set):
                            curr_position = curr_position + 1
                        else:
                            # the sequence ends because we got to a highlighted token that is not consecutive
                            end_seq = curr_position

                            if start_seq <= end_seq:
                                if only_stop_words_in_seq:
                                    highlighted_sequences.append(
                                        (start_seq, end_seq, "r")
                                    )
                                else:
                                    highlighted_sequences.append(
                                        (start_seq, end_seq, "k")
                                    )
                            only_stop_words_in_seq = True
                            curr_position = curr_position + 1
                            start_seq = curr_position

                    else:
                        print("This is an ES highlighting error")
                        curr_position = curr_position + 1
                        start_seq = curr_position
                else:
                    # we start searching another sequence starting with current position
                    start_seq = curr_position
                    curr_position = curr_position + 1
        else:
            end_seq = curr_position - 1
            if start_seq <= end_seq:
                if only_stop_words_in_seq:
                    highlighted_sequences.append((start_seq, end_seq, "r"))
                else:
                    highlighted_sequences.append((start_seq, end_seq, "k"))

            only_stop_words_in_seq = True

            curr_position = curr_position + 1
            start_seq = curr_position

    return highlighted_sequences


def check_if_only_stop_words(tokens, start_seq, end_seq, stop_words):
    # check if a given sequence contains only stop words

    cursor = start_seq
    while cursor <= end_seq:
        curr_token = tokens[cursor]
        dehighlighted_curr_token = get_highlighted_text(curr_token)

        if dehighlighted_curr_token not in stop_words:
            return False

        cursor = cursor + 1

    return True


def get_removable_tags_occurrences(searched_text, original_es_highlight, stop_words):
    sequences = get_sequences(searched_text, original_es_highlight, stop_words)

    occurrences_of_removable_tags = []

    if sequences:
        nb_of_tags = 0
        for seq in sequences:

            if seq[2] == "r":
                cursor = 0
                while cursor <= seq[1] - seq[0]:
                    occurrences_of_removable_tags.append(nb_of_tags + cursor + 1)
                    cursor = cursor + 1

            nb_of_tags = nb_of_tags + seq[1] - int(seq[0]) + 1

    return occurrences_of_removable_tags


def replace_nth_occurrence(string, sub, replacement, n):
    where = [m.start() for m in re.finditer(sub, string)][n - 1]
    before = string[:where]
    after = string[where:]
    after = after.replace(sub, replacement, 1)
    new_string = before + after

    return new_string


def get_processed_text(searched_text, original_es_highlight, stop_words):
    processed_text = original_es_highlight

    removable_tags_occurrences = get_removable_tags_occurrences(
        searched_text, original_es_highlight, stop_words
    )

    nb_of_replacements = 0

    if removable_tags_occurrences:
        for occurrence in removable_tags_occurrences:
            processed_text = replace_nth_occurrence(
                processed_text, "<em>", "", occurrence - nb_of_replacements
            )
            processed_text = replace_nth_occurrence(
                processed_text, "</em>", "", occurrence - nb_of_replacements
            )

            nb_of_replacements = nb_of_replacements + 1

    return processed_text


def adjust_highlight(output, search_term, detected_languages):
    detected_language = ""
    stop_words = []
    if detected_languages:
        # detected_languages can have one or multiple languages
        # if it has multiple languages and among them there is English, we will choose English,
        # else we will choose the first language in the list of detected languages
        if "en" in detected_languages:
            detected_language = "en"
        else:
            detected_language = detected_languages[0]

        stop_words = get_stop_words(detected_language)

    # here we process the "highlight":{"description.highlight":[]} elements from output
    output_hits = output["hits"]["hits"]

    if output_hits:
        counter = 0
        while counter < len(output_hits):
            current_hit = output_hits[counter]
            if "highlight" in current_hit:
                highlights_dict = current_hit["highlight"]
                if "description.highlight" in highlights_dict:
                    highlights_list = highlights_dict["description.highlight"]
                    highlight_counter = 0
                    while highlight_counter < len(highlights_list):
                        original_highlighted_text = highlights_list[highlight_counter]

                        highlights_list[highlight_counter] = get_processed_text(
                            search_term, original_highlighted_text, stop_words
                        )

                        highlight_counter = highlight_counter + 1

            counter = counter + 1

    return output
