"""Top-level launcher used by PyInstaller (it needs a script, not `python -m app.main`).

`--selftest` builds one card without the GUI or Anki, to verify a packaged build.
"""

import sys

from app.main import main


def selftest():
    from app import nlp, pipeline

    nlp.load_model()
    card = pipeline.build_card("Der Hund läuft schnell über die Straße.", "läuft")
    print(card.hidden_sentence, "|", card.answer, "|", card.translation, "|", len(card.audio_bytes), "bytes audio")
    print("warnings:", card.warnings)
    ok = card.answer == "laufen" and card.audio_bytes
    print("SELFTEST", "OK" if ok else "FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        main()
