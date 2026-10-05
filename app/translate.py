"""Free, no-API-key translation of the target word's dictionary form."""

import time
from functools import lru_cache

from deep_translator import GoogleTranslator, MyMemoryTranslator
from deep_translator.exceptions import TooManyRequests


class TranslationError(Exception):
    pass


def _google(word: str) -> str:
    # Google's free endpoint rate-limits aggressively; retry once after a short pause.
    try:
        return GoogleTranslator(source="de", target="en").translate(word)
    except TooManyRequests:
        time.sleep(1.5)
        return GoogleTranslator(source="de", target="en").translate(word)


def _mymemory(word: str) -> str:
    return MyMemoryTranslator(source="de-DE", target="en-GB").translate(word)


@lru_cache(maxsize=1024)
def translate_word(word: str) -> str:
    errors = []
    for backend in (_google, _mymemory):
        try:
            result = backend(word)
            if result:
                return result
        except Exception as e:
            errors.append(f"{backend.__name__.lstrip('_')}: {e}")
    raise TranslationError(f"Could not translate '{word}': " + "; ".join(errors))
