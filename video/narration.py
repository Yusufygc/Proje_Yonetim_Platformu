"""Senaryo metinlerini cümle cümle seslendirir.

Cümle başına ayrı dosya üretildiği için altyazı zamanları tahmin değil, ölçülen süredir.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from timeline import Line, split_sentences
from voice import Narrator

logger = logging.getLogger("demo.narration")


def sentence_pairs(scene: dict[str, Any]) -> list[tuple[str, str]]:
    """(okunacak, altyazıda gösterilecek) cümle çiftleri."""
    spoken = split_sentences(scene["ses"])
    shown = split_sentences(scene.get("altyazi", scene["ses"]))
    if len(spoken) != len(shown):
        raise ValueError(f"{scene['id']}: 'ses' ve 'altyazi' cümle sayısı aynı olmalı")
    return list(zip(spoken, shown))


def narrate(scenario: dict[str, Any], scene_ids: list[str], out_dir: Path) -> dict[str, list[Line]]:
    settings = scenario["seslendirme"]
    narrator = Narrator(settings["ses"], speed=settings["hiz"])
    known = {scene["id"]: scene for scene in scenario["sahneler"]}
    voices: dict[str, list[Line]] = {}
    for scene_id in scene_ids:
        lines = []
        for index, (spoken, shown) in enumerate(sentence_pairs(known[scene_id])):
            target = out_dir / f"{scene_id}_{index}.wav"
            lines.append(Line(shown, target, narrator.speak(spoken, target)))
        voices[scene_id] = lines
        logger.info("%s: %.1f sn ses", scene_id, sum(line.seconds for line in lines))
    return voices
