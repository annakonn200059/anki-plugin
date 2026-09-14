"""Orchestrates NLP, translation, audio and AnkiConnect into one card-creation flow."""

from dataclasses import dataclass, field

from app import anki_client, audio, nlp, translate
from app.constants import (
    FIELD_ANSWER,
    FIELD_AUDIO,
    FIELD_SENTENCE_FULL,
    FIELD_SENTENCE_HIDDEN,
    FIELD_TARGET_WORD_EN,
)


@dataclass
class CardData:
    sentence: str
    hidden_sentence: str
    target_raw: str
    match_type: str
    lemma: str
    pos: str
    answer: str
    translation: str
    audio_bytes: bytes
    warnings: list = field(default_factory=list)


def build_card(sentence: str, target: str) -> CardData:
    span, match_type = nlp.find_target(sentence, target)
    hidden_sentence = nlp.build_hidden_sentence(sentence, span)
    answer, warnings = nlp.compute_answer(span)
    lemma = span.root.lemma_
    pos = span.root.pos_

    if match_type == "lemma":
        warnings = warnings + [
            "Matched via lemma fallback (typed form not found verbatim) — please verify the highlighted word is correct."
        ]
        if pos == "VERB":
            warnings = warnings + [
                "Separable-prefix verbs aren't specially handled — double-check the hidden word and infinitive."
            ]

    try:
        translation = translate.translate_word(lemma)
    except translate.TranslationError as e:
        translation = ""
        warnings = warnings + [str(e)]

    audio_bytes = audio.synth_audio_bytes(sentence)

    return CardData(
        sentence=sentence,
        hidden_sentence=hidden_sentence,
        target_raw=target,
        match_type=match_type,
        lemma=lemma,
        pos=pos,
        answer=answer,
        translation=translation,
        audio_bytes=audio_bytes,
        warnings=warnings,
    )


def confirm_add(card_data: CardData, allow_duplicate: bool = False):
    anki_client.ensure_deck()
    anki_client.ensure_model()
    audio_filename = anki_client.store_media(card_data.audio_bytes)
    fields = {
        FIELD_SENTENCE_FULL: card_data.sentence,
        FIELD_TARGET_WORD_EN: card_data.translation,
        FIELD_SENTENCE_HIDDEN: card_data.hidden_sentence,
        FIELD_ANSWER: card_data.answer,
        FIELD_AUDIO: f"[sound:{audio_filename}]",
    }
    return anki_client.add_note(fields, allow_duplicate=allow_duplicate)
