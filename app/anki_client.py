"""Thin wrapper around the AnkiConnect local HTTP API."""

import base64
import uuid

import requests

from app import constants


class AnkiConnectionError(Exception):
    pass


class AnkiConnectError(Exception):
    pass


class DuplicateNoteError(Exception):
    pass


def invoke(action, **params):
    payload = {"action": action, "version": constants.ANKICONNECT_VERSION, "params": params}
    try:
        response = requests.post(constants.ANKICONNECT_URL, json=payload, timeout=10)
    except requests.exceptions.RequestException:
        raise AnkiConnectionError(
            "Could not connect to Anki. Make sure Anki is running with the AnkiConnect add-on installed."
        )

    result = response.json()
    if len(result) != 2 or "error" not in result or "result" not in result:
        raise AnkiConnectError("Unexpected response from AnkiConnect.")
    if result["error"] is not None:
        raise AnkiConnectError(result["error"])
    return result["result"]


def check_connection():
    invoke("version")


def ensure_deck(deck_name: str = constants.DECK_NAME):
    invoke("createDeck", deck=deck_name)


def ensure_model():
    existing = invoke("modelNames")
    if constants.MODEL_NAME in existing:
        return
    invoke(
        "createModel",
        modelName=constants.MODEL_NAME,
        inOrderFields=constants.MODEL_FIELDS,
        css=constants.MODEL_CSS,
        cardTemplates=[
            {
                "Name": "Sentence Card",
                "Front": constants.MODEL_FRONT_TEMPLATE,
                "Back": constants.MODEL_BACK_TEMPLATE,
            }
        ],
    )


def store_media(audio_bytes: bytes) -> str:
    filename = f"anki-deutsch-{uuid.uuid4().hex}.mp3"
    data_b64 = base64.b64encode(audio_bytes).decode("ascii")
    invoke("storeMediaFile", filename=filename, data=data_b64)
    return filename


def add_note(fields: dict, deck_name: str = constants.DECK_NAME, allow_duplicate: bool = False):
    note = {
        "deckName": deck_name,
        "modelName": constants.MODEL_NAME,
        "fields": fields,
        "tags": [constants.NOTE_TAG],
        "options": {
            "allowDuplicate": allow_duplicate,
            "duplicateScope": "deck",
        },
    }
    try:
        result = invoke("addNote", note=note)
    except AnkiConnectError as e:
        if "duplicate" in str(e).lower():
            raise DuplicateNoteError("This sentence already exists in the deck.")
        raise
    if result is None:
        raise DuplicateNoteError("This sentence already exists in the deck.")
    return result
