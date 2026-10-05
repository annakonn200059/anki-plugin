# anki-deutsch

A small desktop tool that turns a German sentence + a target word into a fully-formed Anki card:
translation, the word's dictionary form (infinitive, or `der/die/das` + noun), a fill-in-the-blank
sentence, and sentence audio — pushed straight into Anki.

## Prerequisites

- [Anki](https://apps.ankiweb.net/) desktop, with the [AnkiConnect](https://ankiweb.net/shared/info/2055492159)
  add-on installed.
- **Anki must be running** whenever you use this app (AnkiConnect exposes a local API on
  `http://localhost:8765` only while Anki is open).
- Python 3.9+.

## Setup

```bash
pip install -r requirements.txt
python -m spacy download de_core_news_sm
```

## Running

```bash
source .venv/bin/activate
python -m app.main
```

## Usage

1. Type a German sentence and the target word as it appears in that sentence (any inflected form
   is fine — the app will find it and figure out the dictionary form).
2. Click **Generate**. Review the preview: hidden sentence, full sentence, the English translation,
   and the computed dictionary form. Both the translation and the dictionary form are editable in
   case the automatic guess (e.g. noun gender) is wrong.
3. Click **Add to Anki**. The card is added to the deck **"Anna + Andrei <3 Deutsch lernen"**
   (created automatically on first use).

The resulting card shows the translation + hidden sentence on the front; flipping it reveals the
dictionary form, the full sentence, and an audio player for the full sentence.
