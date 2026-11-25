"""Videonun saf mantığı. Çalıştırma: python -m pytest video/tests -q (demo bağımlılık grubu gerekir)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

VIDEO_DIR = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(VIDEO_DIR), str(VIDEO_DIR / "capture")]

yaml = pytest.importorskip("yaml", reason="pip install -e .[demo]")

from narration import sentence_pairs  # noqa: E402
from timeline import (  # noqa: E402
    TAIL_FRAMES,
    VOICE_LEAD_FRAMES,
    VOICE_TAIL_FRAMES,
    Line,
    build_timeline,
    place_lines,
    scene_duration,
    to_srt,
)

SCENARIO = yaml.safe_load((VIDEO_DIR / "scenario.yaml").read_text(encoding="utf-8"))


def _line(text: str, seconds: float) -> Line:
    return Line(text, Path("a.wav"), seconds)


def test_scene_duration_when_capture_longer_should_extend_scene() -> None:
    assert scene_duration(2, 30, 90, 0) == 90 + TAIL_FRAMES


def test_scene_duration_when_voice_longer_should_extend_scene() -> None:
    assert scene_duration(2, 30, 30, 200) == 200 + VOICE_TAIL_FRAMES


def test_scene_duration_when_content_shorter_should_keep_target() -> None:
    assert scene_duration(11, 30, 282, 100) == 330


def test_place_lines_when_two_sentences_should_not_leave_subtitle_gap() -> None:
    cues, end = place_lines([_line("Bir.", 2), _line("İki.", 1)], 30)

    assert cues[0]["from"] == VOICE_LEAD_FRAMES
    assert cues[0]["to"] == cues[1]["from"]
    assert end == cues[1]["from"] + 30


def test_place_lines_when_action_starts_later_should_delay_sentence() -> None:
    cues, _ = place_lines([_line("Bir.", 1), _line("İki.", 1)], 30, anchors=[200])

    assert cues[1]["from"] == 200
    assert cues[0]["to"] == 200


def test_place_lines_when_more_marks_than_sentences_should_raise() -> None:
    with pytest.raises(ValueError, match="fazla"):
        place_lines([_line("Bir.", 1)], 30, anchors=[10])


def test_to_srt_when_turkish_text_should_offset_second_scene() -> None:
    cue = {"from": 15, "to": 45, "text": "Çözdüğü ışığı görün."}
    timeline = {"fps": 30, "scenes": [{"duration": 1800, "cues": []}, {"duration": 90, "cues": [cue]}]}

    assert to_srt(timeline) == "1\n00:01:00,500 --> 00:01:01,500\nÇözdüğü ışığı görün.\n"


def test_build_timeline_when_scene_not_captured_should_name_the_command(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="--scene arama"):
        build_timeline(SCENARIO, tmp_path, {"arama": [_line("s.", 1)]})


def test_sentence_pairs_when_subtitle_count_differs_should_raise() -> None:
    with pytest.raises(ValueError, match="cümle sayısı"):
        sentence_pairs({"id": "x", "ses": "Bir. İki.", "altyazi": "Bir."})


def test_scenario_when_loaded_should_have_matching_sentences_in_every_scene() -> None:
    assert all(sentence_pairs(scene) for scene in SCENARIO["sahneler"])


def test_scenes_when_scenario_loaded_should_cover_every_app_scene() -> None:
    from scenes import SCENES

    assert set(SCENES) == {s["id"] for s in SCENARIO["sahneler"] if s["tur"] == "uygulama"}
