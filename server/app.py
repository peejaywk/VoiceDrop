"""
VoiceDrop — drop-server (M0: transcription pipe)

M0 proves the audio -> text path: an HTTP endpoint accepts an uploaded
audio file and transcribes it with Whisper (faster-whisper, local model)
so there is no cloud transcription cost. Later milestones add the Jev
intent/priority router and the Hermes forwarding — not in M0.

Run locally for development:
    uvicorn app:app --host 0.0.0.0 --port 8000

Then POST an audio file to test:
    curl -F "file=@sample.wav" http://localhost:8000/transcribe
"""

import io  # in-memory byte buffer so small clips never touch disk

from fastapi import FastAPI, File, HTTPException, UploadFile
from faster_whisper import WhisperModel

app = FastAPI(title="VoiceDrop drop-server", version="0.1.0")

# --- Whisper model (loaded once, reused for every request) --------------
# "base" is a small local model — a good speed/accuracy balance for M0.
# The model downloads on first load. Swap for "tiny" (faster) or "small"
# (better accuracy) as a one-line change when we need to tune it.
MODEL_SIZE = "base"
_whisper = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")


@app.get("/health")
def health() -> dict:
    """Liveness check so we can confirm the server is up."""
    return {"status": "ok"}


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)) -> dict:
    """
    Accept an uploaded audio file and return its transcription.

    Reads the uploaded bytes, runs them through Whisper, and returns the
    plain-text result and the detected language. Kept in-memory on purpose:
    M0 clips are short voice drops, so streaming is unnecessary complexity.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Read the whole uploaded file into memory (fine for short clips).
    audio_bytes = await file.read()

    # faster-whisper's transcribe() returns (segments, info): a lazy
    # generator of segments first, then the TranscriptionInfo object.
    # NOTE the order — it is very easy to swap these two by accident.
    segments, info = _whisper.transcribe(io.BytesIO(audio_bytes))

    # Whisper hands back segments as an iterator; join them into one plain
    # string, stripping any stray whitespace as we go.
    text = " ".join(segment.text.strip() for segment in segments).strip()

    return {
        "file": file.filename,
        "language": info.language,
        "transcription": text,
    }