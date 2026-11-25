"""Videoyu tek komutla üretir: yakalama, seslendirme, kurgu, ses karışımı, denetim.

Kullanım:
    python video/build.py                          # her şeyi baştan üretir (out/demo.mp4)
    python video/build.py --skip-capture           # çekimleri yeniden kullanır
    python video/build.py --scenes kanca arama --out out/deneme.mp4
"""
from __future__ import annotations

import argparse
import json
import logging
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml
from checks import check
from narration import narrate
from soundtrack import mix, mux
from timeline import build_timeline, to_srt

VIDEO_DIR = Path(__file__).resolve().parent
ROOT = VIDEO_DIR.parent
FRAMES_DIR = VIDEO_DIR / "frames"
CACHE_DIR = VIDEO_DIR / ".cache"
REMOTION_DIR = VIDEO_DIR / "remotion"
GENERATED = REMOTION_DIR / "public" / "generated"
FONTS = ("Medium", "SemiBold", "ExtraBold")
logger = logging.getLogger("demo.build")


def capture(scene_ids: list[str]) -> None:
    for scene_id in scene_ids:
        logger.info("Çekiliyor: %s", scene_id)
        command = [sys.executable, str(VIDEO_DIR / "capture" / "run.py"), "--scene", scene_id]
        subprocess.run(command, check=True)


def prepare_assets(timeline: dict[str, Any]) -> Path:
    """Kurgunun statik dosyalarını `public/generated` altına toplar."""
    GENERATED.mkdir(parents=True, exist_ok=True)
    for weight in FONTS:
        name = f"PlusJakartaSans-{weight}.ttf"
        shutil.copy2(ROOT / "resources" / "fonts" / name, GENERATED / name)
    logo = ["ffmpeg", "-y", "-v", "error", "-i", str(ROOT / "icons" / "256.ico"),
            "-frames:v", "1", str(GENERATED / "logo.png")]
    subprocess.run(logo, check=True)
    for scene in timeline["scenes"]:
        if scene["capture"]:
            shutil.copy2(FRAMES_DIR / f"{scene['id']}.mp4", GENERATED / f"{scene['id']}.mp4")
    props = GENERATED / "timeline.json"
    props.write_text(json.dumps(timeline, ensure_ascii=False), encoding="utf-8")
    return props


def render(props: Path, target: Path) -> None:
    npx = shutil.which("npx")
    if npx is None:
        raise RuntimeError("npx bulunamadı; Node.js kurulu olmalı")
    target.parent.mkdir(parents=True, exist_ok=True)
    command = [npx, "remotion", "render", "src/index.tsx", "Tanitim", str(target),
               f"--props={props}", "--codec=h264", "--pixel-format=yuv420p",
               "--color-space=bt709", "--crf=18", "--muted"]
    subprocess.run(command, cwd=REMOTION_DIR, check=True)


def produce(scenario: dict[str, Any], scene_ids: list[str], target: Path) -> list[str]:
    """Çekimler hazırken videoyu ve `.srt` dosyasını üretir; denetim sorunlarını döndürür."""
    video, music = scenario["video"], scenario["muzik"]
    voices = narrate(scenario, scene_ids, CACHE_DIR / "voice")
    timeline = build_timeline(scenario, FRAMES_DIR, voices)
    silent = CACHE_DIR / "silent.mp4"
    render(prepare_assets(timeline), silent)
    target.parent.mkdir(parents=True, exist_ok=True)
    mux(silent, mix(timeline, music, CACHE_DIR / "mix.wav"), target, music["hedef_lufs"])
    target.with_suffix(".srt").write_text(to_srt(timeline), encoding="utf-8")
    summary, problems = check(
        target, video["genislik"], video["yukseklik"], video["fps"], music["hedef_lufs"]
    )
    for line in summary:
        logger.info(line)
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenes", nargs="*", help="Varsayılan: senaryodaki tüm sahneler")
    parser.add_argument("--skip-capture", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(name)s %(message)s")

    scenario = yaml.safe_load((VIDEO_DIR / "scenario.yaml").read_text(encoding="utf-8"))
    scene_ids = args.scenes or [s["id"] for s in scenario["sahneler"]]
    kinds = {s["id"]: s["tur"] for s in scenario["sahneler"]}
    if not args.skip_capture:
        capture([i for i in scene_ids if kinds[i] == "uygulama"])
    target = VIDEO_DIR / (args.out or scenario["video"]["cikti"])
    problems = produce(scenario, scene_ids, target)
    for problem in problems:
        logger.warning("DENETİM: %s", problem)
    logger.info("Hazır: %s", target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
