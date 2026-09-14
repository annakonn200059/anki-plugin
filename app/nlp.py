"""spaCy-based target-word matching and dictionary-form lookup."""

import spacy

from app import constants

_nlp = None

GENDER_ARTICLE = {"Masc": "der", "Fem": "die", "Neut": "das"}


class TargetNotFoundError(Exception):
    pass


def load_model():
    """Load the spaCy German model once. Call this synchronously at app startup."""
    global _nlp
    if _nlp is None:
        _nlp = spacy.load(constants.SPACY_MODEL)
    return _nlp


def _get_nlp():
    if _nlp is None:
        raise RuntimeError("spaCy model not loaded yet; call load_model() at startup.")
    return _nlp


def find_target(sentence: str, target: str):
    """Find the target word's span in the sentence.

    Tries an exact, case-insensitive, contiguous match first (handles the
    common case and multi-word targets), then falls back to matching by
    lemma if the user typed the word in a different inflected form than it
    appears in the sentence.

    Returns (span, match_type) where match_type is "exact" or "lemma".
    """
    nlp = _get_nlp()
    doc = nlp(sentence)
    target_norm = target.strip()
    if not target_norm:
        raise TargetNotFoundError("Please enter a target word.")

    words = target_norm.split()
    n = len(words)

    for i in range(len(doc) - n + 1):
        span = doc[i:i + n]
        if span.text.lower() == target_norm.lower():
            return span, "exact"

    target_doc = nlp(target_norm)
    if len(target_doc) == 0:
        raise TargetNotFoundError(f"Could not find '{target}' in the sentence.")
    target_lemma = target_doc[0].lemma_.lower()
    for token in doc:
        if token.lemma_.lower() == target_lemma:
            return doc[token.i:token.i + 1], "lemma"

    raise TargetNotFoundError(f"Could not find '{target}' in the sentence.")


def build_hidden_sentence(sentence: str, span) -> str:
    """Blank out the matched span in the original sentence string, preserving
    surrounding punctuation/spacing/capitalization by slicing on char offsets."""
    return sentence[: span.start_char] + "___" + sentence[span.end_char :]


def compute_answer(span):
    """Compute the dictionary-form answer for the matched span.

    Verbs/other parts of speech: bare lemma (spaCy's German lemmatizer
    returns infinitives for verbs). Nouns: lemma prefixed with der/die/das
    based on morphological gender, when determinable.

    Returns (answer_text, warnings).
    """
    token = span.root
    lemma = token.lemma_
    warnings = []
    if token.pos_ in ("NOUN", "PROPN"):
        genders = token.morph.get("Gender")
        if len(genders) == 1 and genders[0] in GENDER_ARTICLE:
            return f"{GENDER_ARTICLE[genders[0]]} {lemma.capitalize()}", warnings
        warnings.append("Could not determine noun gender automatically — please verify the article.")
        return lemma.capitalize(), warnings
    return lemma, warnings
