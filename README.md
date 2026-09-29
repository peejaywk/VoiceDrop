# VoiceDrop — handheld voice assistant for Hermes

A small handheld voice device that captures spoken requests and hands them to
the **Hermes agent** so Hermes turns them into real actions (tasks, vault notes,
agent work).

**Credit / inspiration:** adapted from **"Prompt Boy — I'm done with devices
that do everything"** by **Syntax (syntaxfm)** →
https://www.youtube.com/watch?v=WJCvFqYGrxM

Tracked in the Obsidian vault project note (`VoiceDrop — handheld Hermes voice assistant`).

## Status
**M0 done** — the transcription pipe is built and verified end-to-end.
M1 (hardware) onward is planned but not started.

## Architecture (MVP)
```
Device (ESP32) --audio--> Drop-server --text--> Jev router -> Hermes
```
1. **Device (ESP32-S3-BOX-3, PSRAM)** records a short voice clip on button press
   and POSTs it to the drop-server over LAN. (MVP: LAN + short clips ~10–30 s.)
2. **Drop-server** (this repo, M0) — FastAPI endpoint that receives the audio and
   transcribes it locally with **faster-whisper** (no cloud transcription cost).
3. **Jev router** *(planned)* — cheap question-answer classifier decides the
   task's lane (to-do / research / agent-action), priority, and target project.
   It is the component from the Jev classifier demo, reused here.
4. **Hermes** executes/files the task using the vault + skills.

Jev only **classifies**; Whisper transcribes, Hermes executes. Clean separation.

## Run the M0 server
```bash
cd server
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --host 127.0.0.1 --port 8000
```
From the repo root it's: `uvicorn server.app:app --host 127.0.0.1 --port 8000`.

Test it:
```bash
# health
curl http://127.0.0.1:8000/health
# transcribe an uploaded clip
curl -F "file=@clip.mp3" http://127.0.0.1:8000/transcribe
```
Creates/uses a `data/samples/sample_01.mp3` for testing if present (git-ignored).

## Next milestones
- **M1** — Device records + uploads audio (ESP32 firmware).
- **M2** — Drop-server forwards transcriptions into Hermes.
- **M3** — End-to-end: "add X to my to-dos" lands in the vault tasks.
- **M4** — Polish: enclosure, battery, display, offline buffering (deferred).

## Notes / decisions
- **Memory:** PSRAM-equipped board; no Cloudflare for the LAN MVP. Added later only
  if longer/away-from-home recordings are needed (microSD buffer + retry).
- Per-repo conventions: conventional commits, code authored as **Hermes Agent**.