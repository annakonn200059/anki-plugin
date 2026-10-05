"""Thin wrapper around the AnkiConnect local HTTP API."""

import base64
import uuid

import requests

from app import constants, settings


class AnkiConnectionError(Exception):
    pass


class AnkiConnectError(Exception):
    pass


class DuplicateNoteError(Exception):
    pass


def invoke(action, **params):
    payload = {"action": action, "version": constants.ANKICONNECT_VERSION, "params": params}
    url = settings.ankiconnect_url()
    try:
        response = requests.post(url, json=payload, timeout=10)
    except requests.exceptions.RequestException:
        raise AnkiConnectionError(
            f"Could not connect to Anki at {url}.\n"
            "1) Open Anki and keep it running.\n"
            "2) If you haven't yet: in Anki go to Tools > Add-ons > Get Add-ons, "
            f"enter code {constants.ANKICONNECT_ADDON_CODE}, then restart Anki."
        )

    result = response.json()
    if len(result) != 2 or "error" not in result or "result" not in result:
        raise AnkiConnectError("Unexpected response from AnkiConnect.")
    if result["error"] is not None:
        raise AnkiConnectError(result["error"])
    return result["result"]


def check_connection():
    invoke("version")


def deck_names() -> list:
    return sorted(invoke("deckNames"))


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
