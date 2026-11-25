"""Supertonic 3 ile çevrimdışı Türkçe seslendirme.

Kullanım:  python video/voice.py            # tüm hazır seslerle örnek üretir
"""
from __future__ import annotations

import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

VIDEO_DIR = Path(__file__).resolve().parent
MODEL_DIR = VIDEO_DIR / "assets" / "models" / "supertonic3"
SAMPLES_DIR = VIDEO_DIR / "out" / "ses_ornekleri"
QUALITY_STEPS = 12
SAMPLE_TEXT = (
    "Proje Takip Platformu'nda gününüz ana panelde başlar. "
    "Fikirlerinizi havuzda biriktirin. Çözdüğü problem de projeye taşınır."
)
logger = logging.getLogger("demo.voice")


class Narrator:
    """Modeli bir kez yükler; metni WAV dosyasına çevirir."""

    def __init__(self, voice: str, speed: float = 1.05) -> None:
        if not (MODEL_DIR / "onnx").is_dir():
            raise FileNotFoundError(f"Ses modeli yok: {MODEL_DIR} (kurulum: video/TASARIM.md)")
        os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
        from supertonic import TTS

        self._tts: Any = TTS(model="supertonic-3", model_dir=MODEL_DIR, auto_download=False)
        self._style = self._tts.get_voice_style(voice_name=voice)
        self._speed = speed

    def speak(self, text: str, target: Path) -> float:
        """Metni `target` dosyasına yazar ve süreyi saniye olarak döndürür."""
        wav, duration = self._tts.synthesize(
            text, voice_style=self._style, lang="tr", total_steps=QUALITY_STEPS, speed=self._speed
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        self._tts.save_audio(wav, str(target))
        return float(duration[0])


def voice_names() -> list[str]:
    return sorted(path.stem for path in (MODEL_DIR / "voice_styles").glob("*.json"))


def make_samples() -> Path:
    """Her sesle aynı cümleleri üretir; dinlemesi kolay olsun diye tek dosyada da birleştirir."""
    parts: list[Path] = []
    for name in voice_names():
        narrator = Narrator(name)
        label = SAMPLES_DIR / f"_{name}_etiket.wav"
        sample = SAMPLES_DIR / f"{name}.wav"
        narrator.speak(f"{'Kadın' if name[0] == 'F' else 'Erkek'} ses {name[1]}.", label)
        logger.info("%s: %.1f sn", name, narrator.speak(SAMPLE_TEXT, sample))
        parts += [label, sample]
    return _concat(parts, SAMPLES_DIR / "tum_sesler.mp3")


def _concat(parts: list[Path], target: Path) -> Path:
    inputs = [arg for part in parts for arg in ("-i", str(part))]
    # Her parçanın sonuna kısa sessizlik eklenir ki sesler birbirine karışmasın.
    pads = "".join(f"[{i}:a]apad=pad_dur=0.6[a{i}];" for i in range(len(parts)))
    joined = "".join(f"[a{i}]" for i in range(len(parts)))
    graph = f"{pads}{joined}concat=n={len(parts)}:v=0:a=1[out]"
    command = ["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", graph,
               "-map", "[out]", "-b:a", "160k", str(target)]
    subprocess.run(command, check=True)
    for part in parts:
        if part.name.startswith("_"):
            part.unlink()
    return target


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(name)s %(message)s")
    logger.info("Hazır: %s", make_samples())
    return 0


if __name__ == "__main__":
    sys.exit(main())
