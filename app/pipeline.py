import asyncio
import json
from pathlib import Path

import edge_tts
from faster_whisper import WhisperModel
from pydub import AudioSegment

from . import config
from .audio_utils import extract_audio, speed_up, merge, peaks
from .gender import detect_gender
from .translate import translate_all

_model = None
PEAK_RATE = 20  # timeline waveform bins per second


def get_model():
    global _model
    if _model is None:
        _model = WhisperModel(config.WHISPER_MODEL, compute_type="int8")
    return _model


def tts(text: str, voice: str, out: Path):
    asyncio.run(edge_tts.Communicate(text, voice).save(str(out)))


def process(video: Path, workdir: Path, progress):
    workdir.mkdir(parents=True, exist_ok=True)
    wav = workdir / "audio.wav"

    progress("Audio nikal rahe hain...", 5)
    extract_audio(video, wav)

    progress("Speech-to-text (English)...", 15)
    segs, _ = get_model().transcribe(str(wav), language="en", vad_filter=True)
    segments = [{"start": s.start, "end": s.end, "text": s.text.strip()} for s in segs if s.text.strip()]
    if not segments:
        raise RuntimeError("Video me koi speech nahi mili.")

    progress("Male/Female detect kar rahe hain...", 35)
    for s in segments:
        s["gender"] = detect_gender(wav, s["start"], s["end"])

    progress("Hindi translation...", 45)
    hindi = translate_all([s["text"] for s in segments])
    for s, h in zip(segments, hindi):
        s["hindi"] = h

    total_ms = int(AudioSegment.from_file(wav).duration_seconds * 1000) + 1000
    mix = AudioSegment.silent(duration=total_ms)

    for i, s in enumerate(segments):
        progress(f"Hindi awaaz ban rahi hai ({i+1}/{len(segments)})...", 50 + int(40 * i / len(segments)))
        voice = config.VOICE_FEMALE if s["gender"] == "female" else config.VOICE_MALE
        raw = workdir / f"seg{i}.mp3"
        tts(s["hindi"], voice, raw)
        clip = AudioSegment.from_file(raw)

        nxt = segments[i + 1]["start"] if i + 1 < len(segments) else s["end"] + 3
        slot = max(nxt - s["start"] - 0.1, 0.5) * 1000
        if len(clip) > slot:
            tempo = min(len(clip) / slot, config.MAX_SPEEDUP)
            fast = workdir / f"seg{i}_fast.mp3"
            speed_up(raw, fast, tempo)
            clip = AudioSegment.from_file(fast)
        s["dub_end"] = round(s["start"] + len(clip) / 1000, 2)
        mix = mix.overlay(clip, position=int(s["start"] * 1000))

    progress("Video me merge kar rahe hain...", 93)
    dub = workdir / "dub.wav"
    mix.export(dub, format="wav")

    progress("Timeline bana rahe hain...", 95)
    dur = (total_ms - 1000) / 1000
    (workdir / "peaks.json").write_text(json.dumps({
        "duration": dur, "rate": PEAK_RATE,
        "original": peaks(wav, PEAK_RATE, dur), "dub": peaks(dub, PEAK_RATE, dur),
    }))
    out = workdir / "output.mp4"
    merge(video, dub, out)
    progress("Ho gaya!", 100)
    return out, segments
