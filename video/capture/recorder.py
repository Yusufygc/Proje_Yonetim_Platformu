"""Pencereyi sabit adımla kare kare kaydeder ve imleç/odak bilgisini toplar.

`QSG_FIXED_ANIMATION_STEP` ile her `grabWindow()` çağrısı animasyonları bir ekran yenileme
süresi kadar (60 Hz'de 16,7 ms) ilerletir; kare alma hızı sonucu değiştirmez.
`QTimer` kullanan gecikmeler (ör. bildirim süresi) gerçek saatle akmaya devam eder.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QImage
from PySide6.QtQuick import QQuickWindow
from PySide6.QtWidgets import QApplication

WINDOW_SIZE = (1280, 720)
FRAME_SIZE = (3840, 2160)
FPS = 30
# Bekleme ve imleç sürelerini tek yerden hızlandırır; sahnelerdeki saniyeler bu katsayıyla çarpılır.
TEMPO = 0.7


class Recorder:
    """Kareleri ffmpeg'e akıtır; `<ad>.mp4` ve `<ad>.json` üretir."""

    def __init__(self, window: QQuickWindow, out_dir: Path, name: str) -> None:
        self.window = window
        self.cursor: tuple[float, float] = (WINDOW_SIZE[0] * 0.62, WINDOW_SIZE[1] * 0.7)
        self.frame_count = 0
        self._cursor_track: list[list[float]] = []
        self._clicks: list[int] = []
        self._marks: list[dict[str, object]] = []
        self._json_path = out_dir / f"{name}.json"
        out_dir.mkdir(parents=True, exist_ok=True)
        refresh = QApplication.primaryScreen().refreshRate()
        self._steps = max(1, round(refresh / FPS))
        self._encoder = _start_encoder(out_dir / f"{name}.mp4")
        self._last: QImage | None = None

    def pin_window(self) -> None:
        """Pencereyi çerçevesiz ve sabit boyuta alır; gerçek fare girdisini yok sayar."""
        self.window.setFlags(
            Qt.WindowType.Window
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowTransparentForInput
        )
        self.window.setGeometry(QRect(0, 0, *WINDOW_SIZE))
        self.window.show()
        self.window.requestActivate()

    def settle(self, steps: int = 40) -> None:
        """Kaydetmeden ilerletir (sayfa yükleme, ilk yerleşim)."""
        for _ in range(steps):
            self._advance()

    def frame(self) -> None:
        """Bir çıktı karesi yazar."""
        for _ in range(self._steps):
            self._last = self._advance()
        assert self._last is not None
        self._encoder.stdin.write(bytes(self._last.constBits()))  # type: ignore[union-attr]
        self._cursor_track.append([round(self.cursor[0], 2), round(self.cursor[1], 2)])
        self.frame_count += 1

    def hold(self, seconds: float) -> None:
        for _ in range(round(seconds * TEMPO * FPS)):
            self.frame()

    def mark_click(self) -> None:
        self._clicks.append(self.frame_count)

    def mark(self, kind: str, **data: object) -> None:
        """Kurgunun kullanacağı işaret (kamera odağı, tuş gösterimi)."""
        self._marks.append({"frame": self.frame_count, "kind": kind, **data})

    def close(self) -> None:
        self._encoder.stdin.close()  # type: ignore[union-attr]
        if self._encoder.wait(timeout=600) != 0:
            raise RuntimeError("ffmpeg kareleri videoya çeviremedi")
        payload = {
            "fps": FPS,
            "window": list(WINDOW_SIZE),
            "frames": self.frame_count,
            "cursor": self._cursor_track,
            "clicks": self._clicks,
            "marks": self._marks,
        }
        self._json_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    def _advance(self) -> QImage:
        QApplication.processEvents()
        image = self.window.grabWindow().convertToFormat(QImage.Format.Format_RGB32)
        if (image.width(), image.height()) != FRAME_SIZE:
            raise RuntimeError(
                f"Kare boyutu {image.width()}x{image.height()}, beklenen "
                f"{FRAME_SIZE[0]}x{FRAME_SIZE[1]}. Ekran ölçeklendirmesini kontrol edin."
            )
        return image


def _start_encoder(target: Path) -> subprocess.Popen[bytes]:
    command = [
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{FRAME_SIZE[0]}x{FRAME_SIZE[1]}",
        "-r", str(FPS), "-i", "-",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "14",
        "-pix_fmt", "yuv420p", "-g", str(FPS), str(target),
    ]
    return subprocess.Popen(command, stdin=subprocess.PIPE)
