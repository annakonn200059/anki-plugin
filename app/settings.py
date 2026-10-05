"""Tiny per-user settings file (~/.anki-deutsch.json): last used deck, AnkiConnect URL."""

import json
from pathlib import Path

from app import constants

SETTINGS_PATH = Path.home() / ".anki-deutsch.json"


def _load() -> dict:
    try:
        return json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def get(key: str, default=None):
    return _load().get(key, default)


def set(key: str, value):
    data = _load()
    data[key] = value
    try:
        SETTINGS_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass  # settings are a convenience; never break the app over them


def ankiconnect_url() -> str:
    return get("ankiconnect_url") or constants.ANKICONNECT_URL
