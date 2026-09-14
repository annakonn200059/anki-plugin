"""Free, no-API-key TTS for the full sentence audio via edge-tts."""

import asyncio

import edge_tts

from app import constants


class AudioSynthesisError(Exception):
    pass


def synth_audio_bytes(text: str) -> bytes:
    async def _run():
        communicate = edge_tts.Communicate(text, constants.TTS_VOICE)
        buf = bytearray()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                buf.extend(chunk["data"])
        return bytes(buf)

    try:
        audio_bytes = asyncio.run(_run())
    except Exception as e:
        raise AudioSynthesisError(f"Could not synthesize audio: {e}")

    if not audio_bytes:
        raise AudioSynthesisError("Audio synthesis returned no data.")
    return audio_bytes
