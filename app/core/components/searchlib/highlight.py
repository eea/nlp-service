import logging
import re

import nltk
from langdetect import DetectorFactory, detect_langs

logger = logging.getLogger(__name__)

try:
    from nltk.corpus import stopwords
except Exception:
    nltk.download("stopwords")


DetectorFactory.seed = 0

LANG_CODE_MAPPING = {
    "bg": "bulgarian",
    "cs": "czech",
    "de": "german",
    "el": "greek",
    "en": "english",
    "es": "spanish",
    "et": "estonian",
    "fi": "finnish",
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


class Highlight:
    threshold = 0.8
    default_lang = "en"

    def __init__(self, search_term):
        self.search_term = search_term
        self.highlighted_tokens = []

    @property
    def language(self):
        """
        detect languages in the search term

        languages list can have one or multiple languages
        if it has multiple languages and among them there is English, choose English,
        else choose the first language in the list of detected languages

        :return: language code for search term
        """

        # search_term = {"texts": [self.search_term], "options": {"debug": False}}
        # meth = search_term["options"]["debug"] and detect_langs or detect
        if not self.search_term:
            return self.default_lang

        detected = detect_langs(self.search_term)
        scores = {x.lang: x.prob for x in detected if x.prob > self.threshold}

        if self.default_lang in scores.keys():
            return self.default_lang

        if not scores:
            return self.default_lang

        lang = scores.keys()[0]
        for k in scores.keys():
            if scores[k] > scores[lang]:
                lang = k

        logger.info(f"Matched language {lang} for query: '{self.search_term}'")
        return lang

    @property
    def searched_tokens_positions(self):
        return self._create_positions()

    @property
    def stop_words(self):
        """
        default language is 'english'
        :return: stop_words for the search term language
        """
        if self.language and self.language in LANG_CODE_MAPPING:
            return (
                stopwords.words(LANG_CODE_MAPPING[self.language])
                if self.language
                else stopwords.words("english")
            )
        return []

    def _create_positions(self):
        tokens_position = {}

        if self.search_term is None:
            return tokens_position

        # remove delimiters
        delimiters = ",.!?/&-:; "
        splitter = "[" + "\\".join(delimiters) + "]"
        new_text = " ".join(
            w for w in re.split(splitter, self.search_term.lower()) if w
        )

        # get the tokens
        tokens = new_text.split()

        curr_position = 0

        while curr_position < len(tokens):
            if tokens[curr_position] not in tokens_position:
                tokens_position[tokens[curr_position]] = set()

            tokens_position[tokens[curr_position]].add(curr_position)

            curr_position = curr_position + 1

        return tokens_position

    @staticmethod
    def _is_consecutive_tokens(set_1, set_2):
        for elem in set_1:
            if (elem + 1) in set_2:
                return True
        return False

    @staticmethod
    def _is_highlighted(token):
        if token:
            if ("<em>" in token) and ("</em>" in token):
                return True
        return False

    @staticmethod
    def _get_highlighted(token):
        if token:
            token = token.replace("<em>", "")
            token = token.replace("</em>", "")

        return token

    @staticmethod
    def _add_sequence(start_seq, end_seq, only_stop_words, sequences):
        if start_seq <= end_seq:
            if only_stop_words:
                sequences.append((start_seq, end_seq, "r"))
            else:
                sequences.append((start_seq, end_seq, "k"))

        return sequences

    def _is_consecutive(self, position):
        if position == 0:
            return True
        else:
            curr_token = self.highlighted_tokens[position]
            dehighlighted_curr_token = self._get_highlighted(curr_token)
            curr_token_set = set()
            if dehighlighted_curr_token.lower() in self.searched_tokens_positions:
                curr_token_set = self.searched_tokens_positions[
                    dehighlighted_curr_token.lower()
                ]

            prev_token = self.highlighted_tokens[position - 1]
            dehighlighted_prev_token = self._get_highlighted(prev_token)
            prev_token_set = set()
            if dehighlighted_prev_token.lower() in self.searched_tokens_positions:
                prev_token_set = self.searched_tokens_positions[
                    dehighlighted_prev_token.lower()
                ]

            return self._is_consecutive_tokens(prev_token_set, curr_token_set)

    def _is_highlighted_non_stop_word(self, position):
        if not self._is_highlighted(self.highlighted_tokens[position]):
            return False

        dehighlighted_curr_token = self._get_highlighted(
            self.highlighted_tokens[position]
        )
        if dehighlighted_curr_token.lower() in self.stop_words:
            return False

        return True

    def _sequence_ends(self, start_seq, position):
        if not self._is_highlighted(self.highlighted_tokens[position]):
            return 2
        if not self._is_consecutive(position) and start_seq < position:
            return 1

        return 0

    """
    store a list of tuples (start_seq, end_seq, status) in sequences
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

    def _get_sequences(self, original):
        sequences = []

        if not self.search_term or not original or not self.stop_words:
            return sequences

        self.highlighted_tokens = original.split()

        curr_position = 0

        start_seq = 0
        end_seq = 0
        only_stop_words_in_seq = True

        while curr_position < len(self.highlighted_tokens):
            if self._is_highlighted_non_stop_word(curr_position):
                only_stop_words_in_seq = False

            if self._sequence_ends(start_seq, curr_position):
                end_seq = curr_position - 1
                sequences = self._add_sequence(
                    start_seq, end_seq, only_stop_words_in_seq, sequences
                )
                only_stop_words_in_seq = True
                start_seq = (
                    curr_position + self._sequence_ends(start_seq, curr_position) - 1
                )

            curr_position = curr_position + 1

        return sequences

    def _get_removable_tags(self, original):
        sequences = self._get_sequences(original)

        removable_tags = []

        if sequences:
            nb_of_tags = 0
            for seq in sequences:
                if seq[2] == "r":
                    cursor = 0

                    while cursor <= seq[1] - seq[0]:
                        removable_tags.append(nb_of_tags + cursor + 1)
                        cursor = cursor + 1

                nb_of_tags = nb_of_tags + seq[1] - int(seq[0]) + 1

        return removable_tags

    @staticmethod
    def _replace_nth_occurrence(string, sub, replacement, n):
        where = [m.start() for m in re.finditer(sub, string)][n - 1]
        before = string[:where]
        after = string[where:]
        after = after.replace(sub, replacement, 1)
        new_string = before + after

        return new_string

    def _process_text(self, highlight):
        processed_text = highlight

        removable_tags_occurrences = self._get_removable_tags(highlight)

        nb_of_replacements = 0

        if removable_tags_occurrences:
            for occurrence in removable_tags_occurrences:
                processed_text = self._replace_nth_occurrence(
                    processed_text, "<em>", "", occurrence - nb_of_replacements
                )
                processed_text = self._replace_nth_occurrence(
                    processed_text, "</em>", "", occurrence - nb_of_replacements
                )

                nb_of_replacements = nb_of_replacements + 1

        return processed_text

    def adjust(self, text):
        # here we process the "highlight":{"description.highlight":[]} elements from output
        output_hits = text.get("hits", {}).get("hits", None)

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
                            original_highlighted_text = highlights_list[
                                highlight_counter
                            ]

                            highlights_list[highlight_counter] = self._process_text(
                                original_highlighted_text
                            )

                            highlight_counter += 1

                counter = counter + 1

        return text
