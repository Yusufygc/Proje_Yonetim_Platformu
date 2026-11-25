"""Seslendirme, müzik ve efektleri karıştırır; ses seviyesini dengeleyip videoya ekler."""
from __future__ import annotations

import json
import re
import subprocess
import wave
from pathlib import Path
from typing import Any

import numpy as np
import synth
from synth import RATE, Wave

VOICE_RMS = 0.12
DUCK_DB = -7.0  # Konuşma sırasında müzik bu kadar daha kısılır.
CLICK_GAIN = 0.10
WHOOSH_GAIN = 0.09
CHIME_GAIN = 0.16
VIDEO_DIR = Path(__file__).resolve().parent


def load_audio(path: Path) -> Wave:
    command = ["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(RATE), "-f", "f32le", "-"]
    raw = subprocess.run(command, check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def _db(value: float) -> float:
    return float(10 ** (value / 20))


def _add(track: Wave, sound: Wave, at_frame: int, fps: int, gain: float) -> None:
    start = int(at_frame / fps * RATE)
    piece = sound[: max(0, len(track) - start)]
    track[start : start + len(piece)] += piece * gain


def voice_track(timeline: dict[str, Any], length: int) -> Wave:
    track = np.zeros(length, dtype=np.float32)
    offset = 0
    for scene in timeline["scenes"]:
        for cue in scene["cues"]:
            speech = load_audio(Path(cue["audio"]))
            # Cümleler arası seviye farkı giderilir.
            level = float(np.sqrt(np.mean(speech[np.abs(speech) > 0.01] ** 2)))
            _add(track, speech, offset + cue["from"], timeline["fps"], VOICE_RMS / level)
        offset += scene["duration"]
    return track


def effects_track(timeline: dict[str, Any], length: int) -> Wave:
    track = np.zeros(length, dtype=np.float32)
    fps = timeline["fps"]
    click, whoosh, chime = synth.click(), synth.whoosh(), synth.chime()
    offset = 0
    for scene in timeline["scenes"]:
        if offset:
            _add(track, whoosh, max(0, offset - 7), fps, WHOOSH_GAIN)
        capture = scene["capture"] or {"clicks": [], "marks": []}
        for frame in capture["clicks"]:
            _add(track, click, offset + frame, fps, CLICK_GAIN)
        for mark in capture["marks"]:
            if mark["kind"] == "shortcut":
                _add(track, chime, offset + mark["frame"], fps, CHIME_GAIN)
        offset += scene["duration"]
    return track


def ducking(voice: Wave) -> Wave:
    """Konuşma olan yerlerde DUCK_DB'ye inen, yumuşak geçişli kazanç eğrisi."""
    block = RATE // 20
    blocks = int(np.ceil(len(voice) / block))
    active = np.array([np.abs(voice[i * block : (i + 1) * block]).max() > 0.02 for i in range(blocks)])
    # Komşu bloklara yayılan pencere, kelime aralarında müziğin zıplamasını önler.
    spread = np.convolve(active.astype(np.float32), np.ones(9) / 9, mode="same")
    gain = 1 - np.minimum(1.0, spread * 2) * (1 - _db(DUCK_DB))
    return np.asarray(np.interp(np.arange(len(voice)), np.arange(blocks) * block, gain), dtype=np.float32)


def _background(settings: dict[str, Any], seconds: float, length: int) -> Wave:
    if settings["kaynak"] == "uretilen":
        track = synth.music(seconds)
    else:
        track = load_audio(VIDEO_DIR / "assets" / settings["kaynak"])
        track = np.tile(track, length // max(1, len(track)) + 1)
    track = np.resize(track, length) * _db(settings["seviye_db"])
    fade_in, fade_out = RATE, RATE * 2
    track[:fade_in] *= np.linspace(0, 1, fade_in, dtype=np.float32)
    track[-fade_out:] *= np.linspace(1, 0, fade_out, dtype=np.float32)
    return track


def mix(timeline: dict[str, Any], music: dict[str, Any], target: Path) -> Path:
    seconds = sum(s["duration"] for s in timeline["scenes"]) / timeline["fps"]
    length = int(seconds * RATE)
    voice = voice_track(timeline, length)
    total = voice + effects_track(timeline, length) + _background(music, seconds, length) * ducking(voice)
    total = np.clip(total, -0.98, 0.98)
    target.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(target), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(RATE)
        handle.writeframes((total * 32767).astype(np.int16).tobytes())
    return target


def _measure(audio: Path, loudness: str) -> dict[str, str]:
    command = ["ffmpeg", "-hide_banner", "-nostats", "-i", str(audio),
               "-af", f"{loudness}:print_format=json", "-f", "null", "-"]
    report = subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf-8").stderr
    found = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", report)
    if found is None:
        raise RuntimeError("loudnorm ölçümü okunamadı")
    return dict(json.loads(found.group(0)))


def mux(video: Path, audio: Path, target: Path, lufs: float) -> None:
    """İki geçişli loudnorm: önce ölçer, sonra ölçülen değerlerle sabit kazanç uygular."""
    # Stereoya çevirme ölçümden önce yapılır; sonradan yapılırsa kanal başına seviye 3 dB düşer.
    stereo = "pan=stereo|c0=c0|c1=c0"
    loudness = f"loudnorm=I={lufs}:TP=-1.5:LRA=11"
    seen = _measure(audio, f"{stereo},{loudness}")
    second = (
        f"{stereo},{loudness}:measured_I={seen['input_i']}:measured_TP={seen['input_tp']}"
        f":measured_LRA={seen['input_lra']}:measured_thresh={seen['input_thresh']}"
        f":offset={seen['target_offset']}:linear=true"
    )
    command = ["ffmpeg", "-y", "-v", "error", "-i", str(video), "-i", str(audio),
               "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-af", second,
               "-c:a", "aac", "-b:a", "192k", "-ar", str(RATE),
               "-movflags", "+faststart", str(target)]
    subprocess.run(command, check=True)
