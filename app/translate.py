"""Free, no-API-key translation of the target word's dictionary form."""

from deep_translator import GoogleTranslator


class TranslationError(Exception):
    pass


def translate_word(word: str) -> str:
    try:
        return GoogleTranslator(source="de", target="en").translate(word)
    except Exception as e:
        raise TranslationError(f"Could not translate '{word}': {e}")
