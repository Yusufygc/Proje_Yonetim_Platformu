"""
Ayarlar sayfası — tema, yazı tipi, dil, yedekleme ve dışa aktarma.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app import config
from controllers.settings_controller import SettingsController
from core.managers.preference_manager import PreferenceManager
from core.managers.string_manager import StringManager
from core.managers.theme_manager import ThemeManager
from presentation.dimensions import FontFamily, Size, Spacing
from presentation.utils.i18n import tr

_LANGUAGES: list[tuple[str, str]] = [
    ("Türkçe", "tr"),  # l10n: data — dil adı kendi dilinde gösterilir, çevrilmez
    ("English", "en"),
]

# (id, i18n_key, default_label, koyu-mod dosyası, açık-mod dosyası, önizleme rengi)
# tr() ile paket kartı etiketinde tüketilir.
_THEME_PACKAGES: list[tuple[str, str, str, str, str, str]] = [
    ("slate",   "settings_theme_pkg_slate",   "Slate",   "dark",         "light",         "#678180"),  # l10n: data
    ("indigo",  "settings_theme_pkg_indigo",  "Indigo",  "indigo_dark",  "indigo_light",  "#6366F1"),  # l10n: data
    ("emerald", "settings_theme_pkg_emerald", "Emerald", "emerald_dark", "emerald_light", "#10B981"),  # l10n: data
    ("ocean",   "settings_theme_pkg_ocean",   "Ocean",   "ocean_dark",   "ocean_light",   "#2563EB"),  # l10n: data
    ("rose",    "settings_theme_pkg_rose",    "Rose",    "rose_dark",    "rose_light",    "#F43F5E"),  # l10n: data
    ("violet",  "settings_theme_pkg_violet",  "Violet",  "violet_dark",  "violet_light",  "#8B5CF6"),  # l10n: data
]

# Böyle bir üretkenlik aracı için okunabilir, tanıdık, zaten paketlenmiş
# (resources/fonts/) veya sistemde her yerde bulunan ailelerle sınırlı tutulur;
# QFontDatabase.families() ile tüm sistem fontlarını (Wingdings dahil) listelemek
# gereksiz kalabalık yaratıyordu.
_FONT_CHOICES: list[str] = ["Plus Jakarta Sans", "Inter", "Roboto", "Open Sans", "Segoe UI"]


class SettingsPage(QWidget):
    """Uygulama ayarlarının ve veri yönetiminin yapıldığı sayfa."""

    def __init__(
        self,
        parent: QWidget,
        controller: SettingsController,
        strings: StringManager | None = None,
        prefs: PreferenceManager | None = None,
        theme: ThemeManager | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self._controller = controller
        self._strings = strings or StringManager.instance()
        self._prefs = prefs or PreferenceManager.instance()
        self._theme = theme or ThemeManager.instance()
        self._setup_ui()
        self._connect_signals()

    # ── UI Kurulumu ──────────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea(parent=self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        page = QWidget(parent=scroll)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(Spacing.PAGE, Spacing.PAGE, Spacing.PAGE, Spacing.PAGE)
        layout.setSpacing(Spacing.XXXL)

        title = QLabel(tr("settings_title", "Ayarlar"), parent=page)
        title.setProperty("cssClass", "title-large")
        layout.addWidget(title)

        layout.addWidget(self._build_theme_section(page))
        layout.addWidget(self._build_font_section(page))
        layout.addWidget(self._build_language_section(page))
        layout.addWidget(self._build_data_section(page))

        layout.addStretch()

        version_label = QLabel(
            f"{config.APP_NAME}  —  v{config.APP_VERSION}", parent=page
        )
        version_label.setProperty("cssClass", "text-secondary")
        layout.addWidget(version_label)

        scroll.setWidget(page)
        outer.addWidget(scroll)

    # ── Tema Bölümü ──────────────────────────────────────────────────────────

    def _build_theme_section(self, parent: QWidget) -> QWidget:
        section = QWidget(parent=parent)
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.LG)

        lbl = QLabel(tr("settings_theme_section", "Tema"), parent=section)
        lbl.setProperty("cssClass", "title-small")
        layout.addWidget(lbl)

        # Mod toggle
        mode_row = QHBoxLayout()
        mode_row.setSpacing(Spacing.SM)
        mode_lbl = QLabel(tr("settings_theme_active_mode", "Aktif Mod:"), parent=section)
        mode_lbl.setProperty("cssClass", "text-secondary")
        mode_lbl.setFixedWidth(130)
        mode_row.addWidget(mode_lbl)

        self._btn_dark_mode = QPushButton(
            tr("settings_theme_mode_dark", "● Koyu"), parent=section
        )
        self._btn_light_mode = QPushButton(
            tr("settings_theme_mode_light", "○ Açık"), parent=section
        )
        for btn in (self._btn_dark_mode, self._btn_light_mode):
            btn.setCheckable(True)
            btn.setFixedHeight(Size.BTN_SM_H)
            btn.setProperty("cssClass", "btn-secondary")
        self._btn_dark_mode.clicked.connect(lambda: self._on_mode_changed("dark"))
        self._btn_light_mode.clicked.connect(lambda: self._on_mode_changed("light"))
        mode_row.addWidget(self._btn_dark_mode)
        mode_row.addWidget(self._btn_light_mode)
        mode_row.addStretch()
        layout.addLayout(mode_row)

        # Tema paketi satırı — aktif moda göre (Koyu/Açık) dosya seçilir.
        pkg_lbl = QLabel(
            tr("settings_theme_package_label", "Tema Paketi:"), parent=section
        )
        pkg_lbl.setProperty("cssClass", "text-secondary")
        layout.addWidget(pkg_lbl)
        layout.addWidget(self._build_package_row(section))

        self._refresh_mode_buttons()
        return section

    def _build_package_row(self, parent: QWidget) -> QWidget:
        row_widget = QWidget(parent=parent)
        row = QHBoxLayout(row_widget)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(Spacing.SM)

        self._package_buttons: dict[str, QPushButton] = {}
        for pkg_id, label_key, default_label, dark_stem, light_stem, swatch_hex in _THEME_PACKAGES:
            card = QWidget(parent=row_widget)
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(0, 0, 0, 0)
            card_layout.setSpacing(Spacing.XS)

            swatch = QFrame(parent=card)
            swatch.setFixedSize(14, 14)
            swatch.setStyleSheet(f"background-color: {swatch_hex}; border-radius: 7px;")
            card_layout.addWidget(swatch)

            btn = QPushButton(tr(label_key, default_label), parent=card)
            btn.setCheckable(True)
            btn.setProperty("cssClass", "btn-toggle")
            btn.setFixedHeight(Size.BTN_SM_H)
            btn.clicked.connect(
                lambda checked=False, pid=pkg_id, ds=dark_stem, ls=light_stem: self._on_package_clicked(pid, ds, ls)
            )
            card_layout.addWidget(btn)
            self._package_buttons[pkg_id] = btn

            row.addWidget(card)

        row.addStretch()
        return row_widget

    # ── Font Bölümü ──────────────────────────────────────────────────────────

    def _build_font_section(self, parent: QWidget) -> QWidget:
        section = QWidget(parent=parent)
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.LG)

        lbl = QLabel(tr("settings_font_section", "Yazı Tipi"), parent=section)
        lbl.setProperty("cssClass", "title-small")
        layout.addWidget(lbl)

        # Aile satırı
        ctrl_row = QHBoxLayout()
        ctrl_row.setSpacing(Spacing.LG)

        family_lbl = QLabel(
            tr("settings_font_family", "Yazı Ailesi:"), parent=section
        )
        family_lbl.setProperty("cssClass", "text-secondary")
        family_lbl.setFixedWidth(90)
        ctrl_row.addWidget(family_lbl)

        self._font_combo = QComboBox(parent=section)
        self._font_combo.setMinimumWidth(200)
        self._font_combo.setMinimumHeight(Size.BTN_SM_H)
        self._populate_font_combo()
        ctrl_row.addWidget(self._font_combo)

        ctrl_row.addStretch()
        layout.addLayout(ctrl_row)

        # Önizleme + Uygula — sıkı gruplu tek blok (aile seçiminden görsel olarak ayrışır)
        preview_group = QVBoxLayout()
        preview_group.setSpacing(Spacing.SM)

        prev_lbl = QLabel(
            tr("settings_font_preview", "Önizleme:"), parent=section
        )
        prev_lbl.setProperty("cssClass", "text-secondary")
        preview_group.addWidget(prev_lbl)

        self._font_preview = QLabel(
            tr("settings_font_preview_text", "Hızlı kahverengi tilki — The quick brown fox 0123456789"),
            parent=section,
        )
        self._font_preview.setProperty("cssClass", "text-primary")
        self._font_preview.setStyleSheet("padding: 10px; border-radius: 4px;")
        self._font_preview.setWordWrap(True)
        preview_group.addWidget(self._font_preview)

        apply_row = QHBoxLayout()
        self._font_apply_btn = QPushButton(
            tr("settings_font_apply", "Uygula"), parent=section
        )
        self._font_apply_btn.setProperty("cssClass", "btn-primary")
        self._font_apply_btn.setFixedHeight(Size.BTN_SM_H)
        self._font_apply_btn.clicked.connect(self._on_apply_font)
        apply_row.addWidget(self._font_apply_btn)
        apply_row.addStretch()
        preview_group.addLayout(apply_row)

        layout.addLayout(preview_group)

        self._update_font_preview()

        self._font_combo.currentIndexChanged.connect(self._on_font_changed)

        return section

    # ── Dil Bölümü ───────────────────────────────────────────────────────────

    def _build_language_section(self, parent: QWidget) -> QWidget:
        section = QWidget(parent=parent)
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.LG)

        lang_lbl = QLabel(
            tr("settings_language_section", "Dil"), parent=section
        )
        lang_lbl.setProperty("cssClass", "title-small")
        layout.addWidget(lang_lbl)

        row = QHBoxLayout()
        row.setSpacing(Spacing.XL)
        self._language_combo = QComboBox(parent=section)
        self._language_combo.setMinimumHeight(Size.BTN_SM_H)
        self._language_combo.setMinimumWidth(180)
        current = self._strings.current_language
        for label_text, code in _LANGUAGES:
            self._language_combo.addItem(label_text, code)
        idx = self._language_combo.findData(current)
        if idx >= 0:
            self._language_combo.setCurrentIndex(idx)
        self._language_combo.currentIndexChanged.connect(self._on_language_changed)
        row.addWidget(self._language_combo)
        row.addStretch()
        layout.addLayout(row)

        return section

    # ── Veri Bölümü ──────────────────────────────────────────────────────────

    def _build_data_section(self, parent: QWidget) -> QWidget:
        section = QWidget(parent=parent)
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.LG)

        data_lbl = QLabel(
            tr("settings_data_section", "Veri Yönetimi"), parent=section
        )
        data_lbl.setProperty("cssClass", "title-small")
        layout.addWidget(data_lbl)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(Spacing.XL)

        self._btn_export = QPushButton(
            tr("settings_export_btn", "📤 Tüm Veriyi Dışa Aktar (.json)"), parent=section
        )
        self._btn_export.setProperty("cssClass", "btn-primary")
        self._btn_export.clicked.connect(self._on_export_clicked)
        btn_layout.addWidget(self._btn_export)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        return section

    # ── Yardımcı Metodlar ────────────────────────────────────────────────────

    def _populate_font_combo(self) -> None:
        self._font_combo.blockSignals(True)
        saved = self._prefs.load_font_family()
        select_idx = 0
        for i, fam in enumerate(_FONT_CHOICES):
            self._font_combo.addItem(fam)
            if fam == saved:
                select_idx = i
        self._font_combo.setCurrentIndex(select_idx)
        self._font_combo.blockSignals(False)

    def _refresh_mode_buttons(self) -> None:
        is_light = self._prefs.load_active_mode() == "light"
        self._btn_dark_mode.setChecked(not is_light)
        self._btn_light_mode.setChecked(is_light)
        self._btn_dark_mode.setText(
            tr("settings_theme_mode_dark", "● Koyu") if not is_light
            else tr("settings_theme_mode_dark_off", "○ Koyu")
        )
        self._btn_light_mode.setText(
            tr("settings_theme_mode_light", "● Açık") if is_light
            else tr("settings_theme_mode_light_off", "○ Açık")
        )
        self._refresh_package_buttons()

    def _refresh_package_buttons(self) -> None:
        """Aktif moda göre hangi paketin uygulandığını kart işaretiyle gösterir."""
        is_light = self._prefs.load_active_mode() == "light"
        active_stem = self._prefs.load_light_slot() if is_light else self._prefs.load_dark_slot()
        for pkg_id, _label_key, _default, dark_stem, light_stem, _swatch in _THEME_PACKAGES:
            stem = light_stem if is_light else dark_stem
            self._package_buttons[pkg_id].setChecked(stem == active_stem)

    def _update_font_preview(self) -> None:
        family = self._font_combo.currentText()
        self._font_preview.setFont(QFont(family, FontFamily.DEFAULT_SIZE))

    # ── Tema İşleyicileri ────────────────────────────────────────────────────

    def _on_theme_changed(self, _name: str) -> None:
        self._refresh_mode_buttons()

    def _on_mode_changed(self, mode: str) -> None:
        slot_theme = (
            self._prefs.load_dark_slot()
            if mode == "dark"
            else self._prefs.load_light_slot()
        )
        self._prefs.save_active_mode(mode)
        self._prefs.save_theme(slot_theme)
        self._theme.switch_theme(slot_theme)
        self._refresh_mode_buttons()

    def _on_package_clicked(self, _pkg_id: str, dark_stem: str, light_stem: str) -> None:
        is_light = self._prefs.load_active_mode() == "light"
        stem = light_stem if is_light else dark_stem
        if is_light:
            self._prefs.save_light_slot(stem)
        else:
            self._prefs.save_dark_slot(stem)
        self._prefs.save_theme(stem)
        self._theme.switch_theme(stem)
        self._refresh_package_buttons()

    # ── Font İşleyicileri ────────────────────────────────────────────────────

    def _on_font_changed(self, _idx: int) -> None:
        self._update_font_preview()

    def _on_apply_font(self) -> None:
        family = self._font_combo.currentText()
        self._prefs.save_font_family(family)
        QApplication.instance().setFont(QFont(family, FontFamily.DEFAULT_SIZE))  # type: ignore[union-attr]

    # ── Dil İşleyicisi ───────────────────────────────────────────────────────

    def _on_language_changed(self, index: int) -> None:
        lang_code = self._language_combo.itemData(index)
        if not lang_code or lang_code == self._strings.current_language:
            return
        self._prefs.save_language(lang_code)
        self._strings.set_language(lang_code)

    # ── Veri İşleyicileri ────────────────────────────────────────────────────

    def _connect_signals(self) -> None:
        self._controller.export_completed.connect(self._on_export_completed)
        self._controller.error_occurred.connect(self._on_error)
        self._theme.theme_changed.connect(self._on_theme_changed)

    def _on_export_clicked(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            tr("settings_export_dialog_title", "Veriyi Dışa Aktar"),
            "proje_takip_export.json",
            tr("settings_export_filter", "JSON Dosyası (*.json)"),
        )
        if path:
            self._controller.export_to_json(path)

    def _on_export_completed(self, path: str) -> None:
        QMessageBox.information(
            self,
            tr("success_title", "Başarılı"),
            tr("settings_export_done", "Veriler başarıyla dışa aktarıldı:\n{path}").format(
                path=path
            ),
        )

    def _on_error(self, message: str) -> None:
        QMessageBox.warning(self, tr("error_title", "Hata"), message)
