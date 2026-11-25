"""Senaryo, yakalama kayıtları ve ses sürelerinden zaman çizelgesi ve altyazı üretir."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Kayıt sahne süresinden uzunsa eylem yarıda kesilmesin; sona bu kadar nefes payı eklenir.
TAIL_FRAMES = 12
VOICE_LEAD_FRAMES = 10  # Geçiş bitmeden konuşma başlamasın.
VOICE_GAP_FRAMES = 6
VOICE_TAIL_FRAMES = 14
CUE_LINGER_FRAMES = 10


@dataclass(frozen=True)
class Line:
    """Seslendirilmiş tek cümle."""

    text: str
    audio: Path
    seconds: float


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.?!])\s+", text) if s.strip()]


def place_lines(
    lines: list[Line], fps: int, anchors: list[int] | None = None
) -> tuple[list[dict[str, Any]], int]:
    """Cümleleri sırayla yerleştirir; (altyazı parçaları, sesin bittiği kare) döndürür.

    `anchors[i]`, (i+2). cümlenin anlattığı eylemin başladığı karedir; cümle ondan önce başlamaz.
    """
    marks = anchors or []
    if len(marks) > max(0, len(lines) - 1):
        raise ValueError(f"{len(lines)} cümle için {len(marks)} eylem işareti fazla")
    cues: list[dict[str, Any]] = []
    cursor = VOICE_LEAD_FRAMES
    for index, line in enumerate(lines):
        if 0 < index <= len(marks):
            cursor = max(cursor, marks[index - 1])
        length = round(line.seconds * fps)
        cues.append({"from": cursor, "to": cursor + length, "text": line.text, "audio": str(line.audio)})
        cursor += length + VOICE_GAP_FRAMES
    end = cursor - VOICE_GAP_FRAMES
    # Altyazı bir sonraki cümleye kadar ekranda kalır ki yanıp sönmesin.
    for current, following in zip(cues, cues[1:]):
        current["to"] = following["from"]
    cues[-1]["to"] = end + CUE_LINGER_FRAMES
    return cues, end


def scene_duration(seconds: float, fps: int, captured_frames: int, voice_end: int) -> int:
    """Hedef süre, kayıt ve seslendirmenin (paylarıyla) en uzunu."""
    capture_need = captured_frames + TAIL_FRAMES if captured_frames else 0
    return max(round(seconds * fps), capture_need, voice_end + VOICE_TAIL_FRAMES)


def build_timeline(
    scenario: dict[str, Any], frames_dir: Path, voices: dict[str, list[Line]]
) -> dict[str, Any]:
    """`voices` anahtarlarının sırası sahne sırasıdır."""
    video = scenario["video"]
    known = {scene["id"]: scene for scene in scenario["sahneler"]}
    scenes = [_build_scene(known[i], video["fps"], frames_dir, lines) for i, lines in voices.items()]
    return {
        "fps": video["fps"],
        "width": video["genislik"],
        "height": video["yukseklik"],
        "subtitles": video["altyazi_gomulu"],
        "link": video["baglanti"],
        "aiNote": scenario["seslendirme"]["yapay_zeka_notu"],
        "scenes": scenes,
    }


def to_srt(timeline: dict[str, Any]) -> str:
    fps = timeline["fps"]
    blocks: list[str] = []
    offset = 0
    for scene in timeline["scenes"]:
        for cue in scene["cues"]:
            start, end = _stamp(offset + cue["from"], fps), _stamp(offset + cue["to"], fps)
            blocks.append(f"{len(blocks) + 1}\n{start} --> {end}\n{cue['text']}\n")
        offset += scene["duration"]
    return "\n".join(blocks)


def _stamp(frame: int, fps: int) -> str:
    millis = round(frame * 1000 / fps)
    seconds, millis = divmod(millis, 1000)
    minutes, seconds = divmod(seconds, 60)
    return f"00:{minutes:02d}:{seconds:02d},{millis:03d}"


def _build_scene(
    scene: dict[str, Any], fps: int, frames_dir: Path, lines: list[Line]
) -> dict[str, Any]:
    capture = None
    if scene["tur"] == "uygulama":
        log_path = frames_dir / f"{scene['id']}.json"
        if not log_path.exists():
            raise FileNotFoundError(
                f"{scene['id']} sahnesi çekilmemiş: python video/capture/run.py --scene {scene['id']}"
            )
        capture = json.loads(log_path.read_text(encoding="utf-8"))
        capture["video"] = f"generated/{scene['id']}.mp4"
    anchors = [m["frame"] for m in capture["marks"] if m["kind"] == "say"] if capture else []
    cues, voice_end = place_lines(lines, fps, anchors)
    return {
        "id": scene["id"],
        "kind": scene["tur"],
        "title": scene["baslik"],
        "duration": scene_duration(scene["sure"], fps, capture["frames"] if capture else 0, voice_end),
        "cues": cues,
        "capture": capture,
    }
