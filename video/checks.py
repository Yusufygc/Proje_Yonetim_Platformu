"""Üretilen videonun otomatik denetimi. Akıcılık ve ses tınısı ölçülemez; son izleme kullanıcıdadır."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

TARGET_SECONDS = (60.0, 90.0)
LOUDNESS_TOLERANCE = 1.5


def _ffmpeg_report(video: Path, *filters: str) -> str:
    command = ["ffmpeg", "-hide_banner", "-nostats", "-i", str(video), *filters, "-f", "null", "-"]
    return subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf-8").stderr


def probe(video: Path) -> dict[str, object]:
    command = ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(video)]
    return dict(json.loads(subprocess.run(command, check=True, capture_output=True).stdout))


def _picture_problems(video: Path) -> list[str]:
    report = _ffmpeg_report(video, "-vf", "blackdetect=d=0.4:pix_th=0.03,freezedetect=n=-60dB:d=2")
    black = [f"siyah bölüm: {m}" for m in re.findall(r"black_start:\S+ black_end:\S+", report)]
    return black + [f"donuk bölüm başlangıcı: {m} sn" for m in re.findall(r"freeze_start: (\S+)", report)]


def _loudness(video: Path) -> tuple[float, float]:
    """(bütünleşik LUFS, gerçek tepe dBFS)."""
    report = _ffmpeg_report(video, "-af", "ebur128=peak=true", "-vn")
    integrated = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", report)[-1])
    return integrated, float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", report)[-1])


def check(video: Path, width: int, height: int, fps: int, lufs: float) -> tuple[list[str], list[str]]:
    """(bilgi satırları, sorunlar) döndürür."""
    info = probe(video)
    streams = {s["codec_type"]: s for s in info["streams"]}  # type: ignore[attr-defined]
    picture, sound = streams.get("video"), streams.get("audio")
    if picture is None or sound is None:
        return [], ["görüntü veya ses akışı eksik"]
    seconds = float(info["format"]["duration"])  # type: ignore[index]
    actual = (picture["codec_name"], picture["width"], picture["height"], picture["r_frame_rate"],
              picture["pix_fmt"], sound["codec_name"])
    expected = ("h264", width, height, f"{fps}/1", "yuv420p", "aac")
    problems = [] if actual == expected else [f"biçim {actual}, beklenen {expected}"]
    if not TARGET_SECONDS[0] <= seconds <= TARGET_SECONDS[1]:
        problems.append(f"süre {seconds:.1f} sn, hedef 60-90 sn dışında")
    problems += _picture_problems(video)
    integrated, peak = _loudness(video)
    if abs(integrated - lufs) > LOUDNESS_TOLERANCE:
        problems.append(f"ses seviyesi {integrated} LUFS, hedef {lufs}")
    if peak > -0.5:
        problems.append(f"gerçek tepe {peak} dBFS, kırpılma riski")
    summary = [f"süre {seconds:.1f} sn, {width}x{height}, {fps} fps",
               f"ses {integrated} LUFS, gerçek tepe {peak} dBFS",
               f"boyut {video.stat().st_size / 1_048_576:.1f} MB"]
    return summary, problems
