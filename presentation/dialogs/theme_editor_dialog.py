"""
Tema oluşturma ve düzenleme diyalogu.
Renk token'larını gruplar halinde gösterir; gerçek zamanlı önizleme sunar.
"""
from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.managers.theme_manager import ThemeManager
from presentation.dimensions import Spacing
from presentation.widgets.color_picker_button import ColorPickerButton

_TOKEN_LABELS: dict[str, str] = {
    "background":        "Arkaplan",
    "surface":           "Yüzey",
    "surface_raised":    "Yüksek Yüzey",
    "border":            "Kenar",
    "text_primary":      "Ana Metin",
    "text_secondary":    "İkincil Metin",
    "text_muted":        "Soluk Metin",
    "accent_start":      "Vurgu Başlangıç",
    "accent_end":        "Vurgu Bitiş",
    "icon_on_accent":    "İkon (Vurgu Üzeri)",
    "success":           "Başarı",
    "warning":           "Uyarı",
    "danger":            "Tehlike",
    "sidebar_bg":        "Kenar Çubuğu Zemin",
    "sidebar_active":    "Aktif Öğe",
    "sidebar_text":      "Metin",
    "sidebar_text_active": "Aktif Metin",
    "sidebar_hover_bg":  "Hover Zemin",
    "sidebar_active_bg": "Aktif Zemin",
    "h-sidebar_bg":      "Hover Çubuğu",
    "stage_active":      "Aktif Aşama",
    "stage_done":        "Tamamlanan Aşama",
    "scrollbar_bg":      "Scrollbar Zemin",
    "scrollbar_handle":  "Scrollbar Tutamacı",
}

_TOKEN_GROUPS: list[tuple[str, list[str]]] = [
    ("Arkaplan",      ["background", "surface", "surface_raised", "border"]),
    ("Metin",         ["text_primary", "text_secondary", "text_muted"]),
    ("Vurgu",         ["accent_start", "accent_end", "icon_on_accent"]),
    ("Durum",         ["success", "warning", "danger"]),
    ("Kenar Çubuğu",  ["sidebar_bg", "sidebar_active", "sidebar_text",
                        "sidebar_text_active", "sidebar_hover_bg",
                        "sidebar_active_bg", "h-sidebar_bg"]),
    ("Aşama",         ["stage_active", "stage_done"]),
    ("Scrollbar",     ["scrollbar_bg", "scrollbar_handle"]),
]


class _ThemePreview(QWidget):
    """Çalışma paletini kullanarak mini UI sahnesi çizen widget."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self._palette: dict[str, str] = {}
        self.setFixedHeight(110)
        self.setMinimumWidth(400)

    def update_palette(self, palette: dict[str, str]) -> None:
        self._palette = palette
        self.update()

    def paintEvent(self, _event: object) -> None:  # type: ignore[override]
        if not self._palette:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pal = self._palette

        def c(key: str, fb: str = "#888888") -> QColor:
            return QColor(pal.get(key, fb))

        w, h = self.width(), self.height()
        painter.fillRect(0, 0, w, h, c("background"))

        # Sidebar şeridi
        sw = 52
        painter.fillRect(0, 0, sw, h, c("sidebar_bg"))

        # Aktif nav öğesi
        painter.setBrush(QBrush(c("accent_start")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(6, 12, sw - 12, 16, 3, 3)

        # Pasif nav öğeleri
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(c("sidebar_text"), 1))
        font = QFont()
        font.setPixelSize(6)
        painter.setFont(font)
        for i in range(3):
            painter.drawText(10, 44 + i * 20, "▬  Menü")

        # İçerik alanı — kart
        mx = sw + 14
        cw = min((w - mx - 8) // 2, 160)

        painter.setBrush(QBrush(c("surface")))
        painter.setPen(QPen(c("border"), 1))
        painter.drawRoundedRect(mx, 8, cw, h - 16, 6, 6)

        # Kart başlık
        painter.setPen(QPen(c("text_primary")))
        font.setPixelSize(9)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(mx + 10, 28, "Proje Başlığı")

        font.setBold(False)
        font.setPixelSize(7)
        painter.setFont(font)
        painter.setPen(QPen(c("text_secondary")))
        painter.drawText(mx + 10, 44, "Açıklama metni burada yer alır...")

        # Accent rozet
        ac = c("accent_start")
        bg = QColor(ac)
        bg.setAlpha(40)
        painter.setBrush(QBrush(bg))
        painter.setPen(QPen(ac, 1))
        painter.drawRoundedRect(mx + 10, 54, 46, 13, 3, 3)
        painter.setPen(QPen(ac))
        font.setPixelSize(6)
        painter.setFont(font)
        painter.drawText(mx + 16, 64, "Aktif")

        # Birincil buton
        painter.setBrush(QBrush(c("accent_start")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(mx + 10, 74, 46, 16, 4, 4)
        painter.setPen(QPen(c("icon_on_accent")))
        font.setPixelSize(7)
        painter.setFont(font)
        painter.drawText(mx + 17, 85, "Kaydet")

        # Durum rozetleri (sağ)
        rx = mx + cw + 14
        if rx + 50 < w:
            for i, (key, lbl) in enumerate([("success", "✓ Tamam"),
                                             ("warning", "! Uyarı"),
                                             ("danger",  "✕ Hata")]):
                col = c(key)
                bg2 = QColor(col)
                bg2.setAlpha(35)
                painter.setBrush(QBrush(bg2))
                painter.setPen(QPen(col, 1))
                ry = 12 + i * 30
                painter.drawRoundedRect(rx, ry, 60, 18, 4, 4)
                painter.setPen(QPen(col))
                font.setPixelSize(7)
                painter.setFont(font)
                painter.drawText(rx + 6, ry + 12, lbl)

        painter.end()


class ThemeEditorDialog(QDialog):
    """Tema renklerini düzenleme / yeni tema oluşturma diyalogu."""

    theme_saved = Signal(str)  # kaydedilen temanın adı

    def __init__(
        self,
        theme_manager: ThemeManager,
        theme_name: str | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self._manager = theme_manager
        self._is_new = theme_name is None
        self._original_name = theme_name
        self._preview_active = False
        self._pickers: dict[str, ColorPickerButton] = {}

        if theme_name:
            self._working_palette = self._load_editable_palette(theme_name)
        else:
            self._working_palette = dict(theme_manager.get_palette_copy())

        self.setWindowTitle("Yeni Tema" if self._is_new else f"Düzenle: {theme_name}")
        self.resize(640, 720)
        self.setModal(True)
        self._build_ui()

    # ── Yardımcılar ─────────────────────────────────────────────────────────

    def _load_editable_palette(self, name: str) -> dict[str, str]:
        tm = self._manager
        path = tm._themes_dir / f"{name}.json"
        if not path.exists():
            path = tm._themes_dir / "user" / f"{name}.json"
        if path.exists():
            data: dict = json.loads(path.read_text(encoding="utf-8"))
            return {k: data.get(k, "#888888") for k in _TOKEN_LABELS}
        return dict(tm.get_palette_copy())

    # ── UI Kurulumu ──────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.MD)

        # Yerleşik tema uyarısı
        is_builtin = not self._is_new and self._manager.is_builtin(self._original_name or "")
        if is_builtin:
            notice = QLabel(
                "Yerleşik tema değiştirilemez. Kaydet seçeneği yeni kopya oluşturur.",
                parent=self,
            )
            notice.setStyleSheet(
                "color: #F59E0B; padding: 6px 10px;"
                " background: rgba(245,158,11,0.12); border-radius: 4px;"
            )
            notice.setWordWrap(True)
            layout.addWidget(notice)

        # Tema adı
        name_row = QHBoxLayout()
        name_row.setSpacing(Spacing.MD)
        name_lbl = QLabel("Tema Adı:", parent=self)
        name_lbl.setProperty("cssClass", "text-primary")
        name_lbl.setFixedWidth(80)
        name_row.addWidget(name_lbl)
        self._name_edit = QLineEdit(parent=self)
        self._name_edit.setPlaceholderText("Tema adı girin...")
        if self._original_name:
            default_name = (
                f"{self._original_name}_kopya" if is_builtin else self._original_name
            )
            self._name_edit.setText(default_name)
        name_row.addWidget(self._name_edit)
        layout.addLayout(name_row)

        # Renk editörü kaydırma alanı
        scroll = QScrollArea(parent=self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget(parent=scroll)
        cnt_layout = QVBoxLayout(container)
        cnt_layout.setContentsMargins(0, 0, Spacing.SM, 0)
        cnt_layout.setSpacing(Spacing.SM)

        for group_name, tokens in _TOKEN_GROUPS:
            cnt_layout.addWidget(self._build_group(group_name, tokens))

        cnt_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll, 1)

        # Önizleme
        prev_lbl = QLabel("Önizleme", parent=self)
        prev_lbl.setProperty("cssClass", "text-secondary")
        layout.addWidget(prev_lbl)

        self._preview = _ThemePreview(parent=self)
        self._preview.update_palette(self._working_palette)
        layout.addWidget(self._preview)

        # Alt butonlar
        btn_row = QHBoxLayout()
        btn_row.setSpacing(Spacing.MD)

        self._preview_btn = QPushButton("Geçici Uygula", parent=self)
        self._preview_btn.setProperty("cssClass", "btn-secondary")
        self._preview_btn.clicked.connect(self._on_preview_toggle)
        btn_row.addWidget(self._preview_btn)

        btn_row.addStretch()

        cancel_btn = QPushButton("İptal", parent=self)
        cancel_btn.setProperty("cssClass", "btn-secondary")
        cancel_btn.clicked.connect(self._on_cancel)
        btn_row.addWidget(cancel_btn)

        save_btn = QPushButton("Kaydet", parent=self)
        save_btn.setProperty("cssClass", "btn-primary")
        save_btn.clicked.connect(self._on_save)
        btn_row.addWidget(save_btn)

        layout.addLayout(btn_row)

    def _build_group(self, title: str, tokens: list[str]) -> QFrame:
        frame = QFrame(parent=self)
        frame.setProperty("cssClass", "panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(Spacing.MD, Spacing.SM, Spacing.MD, Spacing.MD)
        layout.setSpacing(Spacing.SM)

        lbl = QLabel(title, parent=frame)
        lbl.setProperty("cssClass", "section-header")
        layout.addWidget(lbl)

        grid = QGridLayout()
        grid.setHorizontalSpacing(Spacing.XL)
        grid.setVerticalSpacing(Spacing.SM)

        for i, token in enumerate(tokens):
            row, col = divmod(i, 2)

            cell_widget = QWidget(parent=frame)
            cell = QHBoxLayout(cell_widget)
            cell.setContentsMargins(0, 0, 0, 0)
            cell.setSpacing(Spacing.SM)

            picker = ColorPickerButton(
                color=self._working_palette.get(token, "#888888"),
                parent=frame,
            )
            picker.color_changed.connect(
                lambda clr, t=token: self._on_color_changed(t, clr)
            )
            self._pickers[token] = picker
            cell.addWidget(picker)

            token_lbl = QLabel(_TOKEN_LABELS.get(token, token), parent=frame)
            token_lbl.setProperty("cssClass", "text-secondary")
            token_lbl.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
            )
            cell.addWidget(token_lbl)

            grid.addWidget(cell_widget, row, col)

        layout.addLayout(grid)
        return frame

    # ── Sinyal İşleyicileri ─────────────────────────────────────────────────

    def _on_color_changed(self, token: str, color: str) -> None:
        self._working_palette[token] = color
        self._preview.update_palette(self._working_palette)
        if self._preview_active:
            self._apply_preview()

    def _on_preview_toggle(self) -> None:
        if self._preview_active:
            self._preview_active = False
            self._preview_btn.setText("Geçici Uygula")
            self._manager.restore_preview()
        else:
            self._preview_active = True
            self._preview_btn.setText("Önizlemeyi Geri Al")
            self._apply_preview()

    def _apply_preview(self) -> None:
        full = ThemeManager.derive_alpha_tokens(dict(self._working_palette))
        self._manager.preview_palette(full)

    def _on_save(self) -> None:
        name = self._name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Hata", "Tema adı boş olamaz.")
            return

        if self._preview_active:
            self._manager.restore_preview()
            self._preview_active = False

        full_palette = ThemeManager.derive_alpha_tokens(dict(self._working_palette))
        existing_names = [t["name"] for t in self._manager.list_themes()]

        is_builtin_src = not self._is_new and self._manager.is_builtin(
            self._original_name or ""
        )

        if self._is_new or is_builtin_src:
            if name in existing_names:
                QMessageBox.warning(self, "Hata", "Bu isimde bir tema zaten mevcut.")
                return
            self._manager.create_theme(name, full_palette)
        else:
            # Kullanıcı teması düzenleme
            if name != self._original_name:
                if name in existing_names:
                    QMessageBox.warning(self, "Hata", "Bu isimde bir tema zaten mevcut.")
                    return
                self._manager.create_theme(name, full_palette)
                self._manager.delete_theme(self._original_name or "")
            else:
                self._manager.update_theme(name, full_palette)

        self._manager.switch_theme(name)
        self.theme_saved.emit(name)
        self.accept()

    def _on_cancel(self) -> None:
        if self._preview_active:
            self._manager.restore_preview()
            self._preview_active = False
        self.reject()

    def closeEvent(self, event: object) -> None:  # type: ignore[override]
        if self._preview_active:
            self._manager.restore_preview()
            self._preview_active = False
        super().closeEvent(event)  # type: ignore[arg-type]
