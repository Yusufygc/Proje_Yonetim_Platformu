"""
Sesli metin girişi için toggle buton ve QLineEdit/QTextEdit sarmalama yardımcısı.

VoiceInputButton: mikrofon ikonu; tıklandığında TranscriptionWorker başlatır
veya durdurur. Final tanıma sonucunu hedef alana yazar (tek satır veya çok satır).

attach_voice_button(): hedef alan + VoiceInputButton'ı HBox container içinde
döndürür — mevcut konvansiyona uygun, dialog layout'larına tek satırla eklenir.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Union

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QTextEdit, QWidget

VoiceTarget = Union[QLineEdit, QTextEdit]

from core.managers.icon_manager import Icons
from core.workers.transcription_worker import TranscriptionWorker
from presentation.utils.i18n import tr
from presentation.widgets.icon_action_button import IconActionButton

if TYPE_CHECKING:
    from services.speech.speech_to_text_service import SpeechToTextService

logger = logging.getLogger(__name__)

_STYLE_IDLE = (
    "QPushButton { background: transparent; border: none; border-radius: 6px; padding: 0; }"
    " QPushButton:hover { background-color: rgba(128, 128, 128, 0.18); }"
)
_STYLE_RECORDING = (
    "QPushButton { background: rgba(220, 53, 69, 0.20); border: none; border-radius: 6px; padding: 0; }"
    " QPushButton:hover { background: rgba(220, 53, 69, 0.30); }"
)
_COLOR_RECORDING = "#dc3545"


def _resolve_theme_color(key: str, fallback: str) -> str:
    """Tema rengi çeker; container henüz hazır değilse fallback döner."""
    try:
        from app.di_container import DIContainer  # noqa: PLC0415
        return DIContainer.instance().theme.color(key)
    except (AssertionError, AttributeError, RuntimeError):
        return fallback


class VoiceInputButton(IconActionButton):
    """
    Mikrofon toggle butonu.

    İlk tıklamada dinlemeyi başlatır, ikinci tıklamada durdurur.
    Final tanıma sonuçları boşlukla ayrılarak hedef alana eklenir.
    """

    def __init__(self, target: VoiceTarget, parent: QWidget | None = None) -> None:
        idle_color = _resolve_theme_color("text_muted", "#9ca3af")
        hover_color = _resolve_theme_color("text_primary", "#e5e7eb")
        super().__init__(
            icon_name=Icons.MIC,
            idle_color=idle_color,
            hover_color=hover_color,
            tooltip=tr("voice_button_idle_tooltip", "Sesle yaz"),
            parent=parent,
        )
        self._target = target
        self._worker: TranscriptionWorker | None = None
        self._is_recording = False
        self.clicked.connect(self._toggle)

    # ── Toggle mantığı ──────────────────────────────────────────────────────

    def _toggle(self) -> None:
        if self._is_recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self) -> None:
        service = self._get_speech_service()
        if service is None:
            return

        self._worker = TranscriptionWorker(service=service)
        self._worker.signals.final.connect(self._on_final_text)
        self._worker.signals.error.connect(self._on_error)
        self._worker.signals.finished.connect(self._on_finished)
        self._worker.start()

        self._is_recording = True
        self._apply_recording_style(recording=True)
        self.setToolTip(tr("voice_button_recording_tooltip", "Dinleniyor… durdurmak için tıkla"))

    def _stop_recording(self) -> None:
        if self._worker is not None:
            self._worker.stop()
        self._is_recording = False
        self._apply_recording_style(recording=False)
        self.setToolTip(tr("voice_button_idle_tooltip", "Sesle yaz"))

    def _get_speech_service(self) -> SpeechToTextService | None:
        """DI container'dan konuşma servisini çeker; hata durumunda toast atar."""
        try:
            from app.di_container import DIContainer  # noqa: PLC0415
            return DIContainer.instance().speech_service  # type: ignore[return-value]
        except (AttributeError, RuntimeError) as exc:
            self._publish_error(
                tr("voice_error_service", "Sesli komut servisi başlatılamadı.")
            )
            logger.error("Konuşma servisi alınamadı: %s", exc)
            return None

    # ── Görsel durum ─────────────────────────────────────────────────────────

    def _apply_recording_style(self, recording: bool) -> None:
        if recording:
            self.setStyleSheet(_STYLE_RECORDING)
            self._set_icon(_COLOR_RECORDING)
        else:
            self.setStyleSheet(_STYLE_IDLE)
            self._set_icon(self._idle_color)

    def enterEvent(self, event: object) -> None:  # type: ignore[override]
        if not self._is_recording:
            super().enterEvent(event)

    def leaveEvent(self, event: object) -> None:  # type: ignore[override]
        if not self._is_recording:
            super().leaveEvent(event)

    # ── Sinyal slotları ──────────────────────────────────────────────────────

    def _on_final_text(self, text: str) -> None:
        if isinstance(self._target, QLineEdit):
            self._insert_into_line_edit(text)
        else:
            self._insert_into_text_edit(text)

    def _insert_into_line_edit(self, text: str) -> None:
        before_cursor = self._target.text()[: self._target.cursorPosition()]
        prefix = " " if before_cursor and not before_cursor.endswith(" ") else ""
        self._target.insert(prefix + text)

    def _insert_into_text_edit(self, text: str) -> None:
        cursor = self._target.textCursor()
        current = self._target.toPlainText()
        prefix = " " if current and not current.endswith(" ") else ""
        cursor.insertText(prefix + text)
        self._target.setTextCursor(cursor)

    def _on_error(self, message: str) -> None:
        logger.error("STT hatası: %s", message)
        self._publish_error(message)
        # Worker hata verdiğinde dinlemeyi otomatik durdur
        self._is_recording = False
        self._apply_recording_style(recording=False)
        self.setToolTip(tr("voice_button_idle_tooltip", "Sesle yaz"))

    def _on_finished(self) -> None:
        # Hata sonrası zaten durdurulmuş olabilir; idempotent çağrı güvenli.
        if self._is_recording:
            self._stop_recording()
        self._worker = None

    @staticmethod
    def _publish_error(message: str) -> None:
        try:
            from core.events.event_bus import EventBus  # noqa: PLC0415
            EventBus.instance().publish("toast.show", message=message, type_="warning")
        except Exception:  # noqa: BLE001
            logger.warning("Toast gönderilemedi: %s", message)


def attach_voice_button(target: VoiceTarget, parent: QWidget) -> QWidget:
    """
    QLineEdit veya QTextEdit'i sağında VoiceInputButton ile sarmalayan container döndürür.

    Çağrı yeri:
        layout.addWidget(self._desc_edit)
        →
        layout.addWidget(attach_voice_button(self._desc_edit, form_widget))

    target otomatik olarak container'a reparent edilir (Qt normal davranışı).
    Tek satırlı QLineEdit'lerde buton dikey ortalanır; çok satırlı QTextEdit'lerde üste hizalanır.
    """
    container = QWidget(parent=parent)
    h_layout = QHBoxLayout(container)
    h_layout.setContentsMargins(0, 0, 0, 0)
    h_layout.setSpacing(4)
    h_layout.addWidget(target, 1)
    mic_btn = VoiceInputButton(target=target, parent=container)
    align = Qt.AlignmentFlag.AlignVCenter if isinstance(target, QLineEdit) else Qt.AlignmentFlag.AlignTop
    h_layout.addWidget(mic_btn, 0, align)
    return container
