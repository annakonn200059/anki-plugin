ANKICONNECT_URL = "http://localhost:8765"
ANKICONNECT_VERSION = 6

DECK_NAME = "Anna + Andrei <3 Deutsch lernen"
MODEL_NAME = "DE Sentence Vocab v2 (Anna+Andrei)"

FIELD_SENTENCE_FULL = "SentenceFull"
FIELD_TARGET_WORD_EN = "TargetWordEN"
FIELD_SENTENCE_HIDDEN = "SentenceHidden"
FIELD_ANSWER = "Answer"
FIELD_AUDIO = "Audio"

# SentenceHidden is listed first because AnkiConnect's addNote dedups on the
# model's first field. Using the hidden sentence (rather than the full one)
# means two different target words from the same sentence are NOT treated as
# duplicates (their blanked position differs), while re-adding the exact same
# word from the exact same sentence still is.
MODEL_FIELDS = [
    FIELD_SENTENCE_HIDDEN,
    FIELD_SENTENCE_FULL,
    FIELD_TARGET_WORD_EN,
    FIELD_ANSWER,
    FIELD_AUDIO,
]

MODEL_CSS = """
.card {
    font-family: arial;
    font-size: 22px;
    text-align: center;
    color: #1b1b1b;
    background-color: #fafafa;
}
.translation { font-size: 18px; color: #555; margin-bottom: 12px; }
.sentence { margin: 10px 0; }
.answer { font-size: 28px; font-weight: bold; color: #2f6f4f; margin: 10px 0; }
"""

MODEL_FRONT_TEMPLATE = (
    '<div class="translation">{{TargetWordEN}}</div>'
    '<div class="sentence">{{SentenceHidden}}</div>'
)

MODEL_BACK_TEMPLATE = (
    "{{FrontSide}}"
    '<hr id="answer">'
    '<div class="answer">{{Answer}}</div>'
    '<div class="sentence full">{{SentenceFull}}</div>'
    '<div class="audio">{{Audio}}</div>'
)

SPACY_MODEL = "de_core_news_sm"
TTS_VOICE = "de-DE-KatjaNeural"

NOTE_TAG = "anki-deutsch-app"
