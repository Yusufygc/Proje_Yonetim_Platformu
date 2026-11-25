"""Müzik ve ses efektlerini sıfırdan üretir; üçüncü taraf ses kaydı kullanılmaz."""
from __future__ import annotations

import numpy as np
import numpy.typing as npt

RATE = 48_000
TEMPO_BPM = 96
# Am - F - C - G (MIDI notaları); her akor bir ölçü sürer.
CHORDS = ((57, 60, 64), (53, 57, 60), (55, 60, 64), (55, 59, 62))

Wave = npt.NDArray[np.float32]


def _freq(note: int) -> float:
    return 440.0 * 2 ** ((note - 69) / 12)


def _times(seconds: float) -> Wave:
    return (np.arange(int(seconds * RATE)) / RATE).astype(np.float32)


def _tone(note: int, seconds: float, attack: float, decay: float) -> Wave:
    t = _times(seconds)
    f = _freq(note)
    # Hafif akort farkı ve zayıf üst harmonik sinüsü daha sıcak yapar.
    body = np.sin(2 * np.pi * f * t) + 0.6 * np.sin(2 * np.pi * f * 1.004 * t)
    body += 0.18 * np.sin(2 * np.pi * f * 2 * t)
    envelope = np.minimum(1.0, t / attack) * np.exp(-t / decay)
    release = np.minimum(1.0, (seconds - t) / 0.08)
    return np.asarray((body * envelope * release), dtype=np.float32)


def _kick() -> Wave:
    t = _times(0.28)
    sweep = 95 * np.exp(-t * 22) + 45
    return np.asarray((np.sin(2 * np.pi * np.cumsum(sweep) / RATE) * np.exp(-t * 14)), dtype=np.float32)


def _add(track: Wave, sound: Wave, at_seconds: float, gain: float) -> None:
    start = int(at_seconds * RATE)
    if start >= len(track):
        return
    piece = sound[: len(track) - start]
    track[start : start + len(piece)] += piece * gain


def music(seconds: float) -> Wave:
    """Yumuşak ped, arpej ve hafif vuruştan oluşan fon; tepe değeri 1'e ölçeklenir."""
    beat = 60 / TEMPO_BPM
    bar = beat * 4
    track = np.zeros(int(seconds * RATE), dtype=np.float32)
    kick = _kick()
    for index in range(int(seconds / bar) + 1):
        chord = CHORDS[index % len(CHORDS)]
        start = index * bar
        for note in chord:
            _add(track, _tone(note, bar + 0.4, 0.6, 3.2), start, 0.11)
        _add(track, _tone(chord[0] - 24, bar, 0.05, 1.6), start, 0.20)
        for step in range(8):
            note = chord[(step * 2) % 3] + 12
            _add(track, _tone(note, 0.5, 0.008, 0.16), start + step * beat / 2, 0.07)
        # İlk iki ölçü vuruşsuz: giriş sakin başlasın.
        if index >= 2:
            for quarter in (0, 2):
                _add(track, kick, start + quarter * beat, 0.30)
    return (track / max(1e-6, float(np.abs(track).max()))).astype(np.float32)


def click() -> Wave:
    t = _times(0.05)
    noise = np.random.default_rng(3).standard_normal(len(t)).astype(np.float32)
    tick = np.sin(2 * np.pi * 1800 * t) * 0.7 + noise * 0.3
    return np.asarray((tick * np.exp(-t * 120)), dtype=np.float32)


def whoosh() -> Wave:
    t = _times(0.45)
    noise = np.random.default_rng(11).standard_normal(len(t)).astype(np.float32)
    # Hareketli ortalama gürültüyü yumuşatır (basit alçak geçiren süzgeç).
    soft = np.convolve(noise, np.ones(24, dtype=np.float32) / 24, mode="same")
    return np.asarray((soft * np.sin(np.pi * t / t[-1]) ** 2), dtype=np.float32)


def chime() -> Wave:
    first = _tone(81, 0.35, 0.005, 0.12)
    second = _tone(88, 0.35, 0.005, 0.12)
    both = np.zeros(int(0.45 * RATE), dtype=np.float32)
    _add(both, first, 0.0, 0.5)
    _add(both, second, 0.09, 0.5)
    return both
