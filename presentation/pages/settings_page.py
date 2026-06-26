"""
Ayarlar sayfası — tema, yazı tipi, dil, yedekleme ve dışa aktarma.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from app import config
from controllers.settings_controller import SettingsController
from core.managers.preference_manager import PreferenceManager
from core.managers.string_manager import StringManager
from core.managers.theme_manager import ThemeManager
from presentation.dialogs.theme_editor_dialog import ThemeEditorDialog
from presentation.dimensions import Size, Spacing
from presentation.utils.i18n import tr

_LANGUAGES: list[tuple[str, str]] = [
    ("Türkçe", "tr"),
    ("English", "en"),
]

_ACCENT_PRESETS: list[tuple[str, str]] = [
    ("#6366F1", "İndigo"),
    ("#0EA5E9", "Mavi"),
    ("#10B981", "Yeşil"),
    ("#F59E0B", "Amber"),
    ("#EC4899", "Pembe"),
    ("#678180", "Deniz"),
]


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

        # Slot satırları
        layout.addWidget(self._build_slot_row(
            section,
            tr("settings_theme_dark_slot", "Koyu Mod Teması:"),
            "dark",
        ))
        layout.addWidget(self._build_slot_row(
            section,
            tr("settings_theme_light_slot", "Açık Mod Teması:"),
            "light",
        ))

        # Hızlı Vurgu rengi
        accent_row = QHBoxLayout()
        accent_row.setSpacing(Spacing.SM)
        accent_lbl = QLabel(
            tr("settings_theme_quick_accent", "Hızlı Vurgu:"), parent=section
        )
        accent_lbl.setProperty("cssClass", "text-secondary")
        accent_lbl.setFixedWidth(130)
        accent_row.addWidget(accent_lbl)

        for hex_color, label in _ACCENT_PRESETS:
            chip = QPushButton(parent=section)
            chip.setFixedSize(28, 28)
            chip.setToolTip(label)
            chip.setStyleSheet(
                f"QPushButton {{ background: {hex_color}; border-radius: 14px;"
                f" border: 2px solid transparent; }}"
                f"QPushButton:hover {{ border: 2px solid rgba(255,255,255,0.6); }}"
            )
            chip.clicked.connect(
                lambda checked, hx=hex_color: self._on_accent_quick_change(hx)
            )
            accent_row.addWidget(chip)
        accent_row.addStretch()
        layout.addLayout(accent_row)

        # Yeni / İçe Aktar satırı
        action_row = QHBoxLayout()
        action_row.setSpacing(Spacing.SM)

        new_btn = QPushButton(
            tr("settings_theme_new_btn", "+ Yeni Tema"), parent=section
        )
        new_btn.setProperty("cssClass", "btn-primary")
        new_btn.clicked.connect(self._on_new_theme)
        action_row.addWidget(new_btn)

        import_btn = QPushButton(
            tr("settings_theme_import_btn", "İçe Aktar .json"), parent=section
        )
        import_btn.setProperty("cssClass", "btn-secondary")
        import_btn.clicked.connect(self._on_import_theme)
        action_row.addWidget(import_btn)

        action_row.addStretch()
        layout.addLayout(action_row)

        self._refresh_mode_buttons()
        return section

    def _build_slot_row(
        self, parent: QWidget, label_text: str, slot_key: str
    ) -> QWidget:
        row_widget = QWidget(parent=parent)
        row = QHBoxLayout(row_widget)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(Spacing.SM)

        lbl = QLabel(label_text, parent=row_widget)
        lbl.setProperty("cssClass", "text-secondary")
        lbl.setFixedWidth(130)
        row.addWidget(lbl)

        combo = QComboBox(parent=row_widget)
        combo.setMinimumWidth(150)
        combo.setMinimumHeight(Size.BTN_SM_H)
        self._populate_theme_combo(combo, slot_key)
        row.addWidget(combo)

        edit_btn = QPushButton(tr("settings_theme_edit_btn", "Düzenle"), parent=row_widget)
        edit_btn.setProperty("cssClass", "btn-secondary")
        edit_btn.setFixedHeight(Size.BTN_SM_H)
        row.addWidget(edit_btn)

        copy_btn = QPushButton(tr("settings_theme_copy_btn", "Kopyala"), parent=row_widget)
        copy_btn.setProperty("cssClass", "btn-secondary")
        copy_btn.setFixedHeight(Size.BTN_SM_H)
        row.addWidget(copy_btn)

        export_btn = QPushButton("↑", parent=row_widget)
        export_btn.setProperty("cssClass", "btn-secondary")
        export_btn.setFixedSize(Size.BTN_SM_H, Size.BTN_SM_H)
        export_btn.setToolTip(tr("settings_theme_export_btn", "Dışa Aktar"))
        row.addWidget(export_btn)

        del_btn = QPushButton(tr("settings_theme_delete_btn", "Sil"), parent=row_widget)
        del_btn.setProperty("cssClass", "btn-secondary")
        del_btn.setFixedHeight(Size.BTN_SM_H)
        row.addWidget(del_btn)

        row.addStretch()

        # Bağlantılar
        combo.currentIndexChanged.connect(
            lambda _idx, s=slot_key, cb=combo: self._on_slot_changed(s, cb)
        )
        edit_btn.clicked.connect(
            lambda checked, s=slot_key, cb=combo: self._on_edit_theme(cb.currentData())
        )
        copy_btn.clicked.connect(
            lambda checked, s=slot_key, cb=combo: self._on_copy_theme(cb.currentData(), cb)
        )
        export_btn.clicked.connect(
            lambda checked, cb=combo: self._on_export_theme(cb.currentData())
        )
        del_btn.clicked.connect(
            lambda checked, s=slot_key, cb=combo: self._on_delete_theme(cb.currentData(), s, cb)
        )

        # Combo referanslarını sakla
        if slot_key == "dark":
            self._dark_combo = combo
            self._dark_del_btn = del_btn
        else:
            self._light_combo = combo
            self._light_del_btn = del_btn

        self._update_del_btn_state(del_btn, combo.currentData() or "")

        combo.currentIndexChanged.connect(
            lambda _idx, b=del_btn, cb=combo: self._update_del_btn_state(b, cb.currentData() or "")
        )

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

        # Aile + boyut satırı
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

        size_lbl = QLabel(
            tr("settings_font_size", "Boyut:"), parent=section
        )
        size_lbl.setProperty("cssClass", "text-secondary")
        ctrl_row.addWidget(size_lbl)

        self._font_size_spin = QSpinBox(parent=section)
        self._font_size_spin.setRange(7, 20)
        self._font_size_spin.setSuffix(" pt")
        self._font_size_spin.setFixedHeight(Size.BTN_SM_H)
        self._font_size_spin.setFixedWidth(72)
        self._font_size_spin.setValue(self._prefs.load_font_size())
        ctrl_row.addWidget(self._font_size_spin)

        ctrl_row.addStretch()
        layout.addLayout(ctrl_row)

        # Önizleme
        prev_lbl = QLabel(
            tr("settings_font_preview", "Önizleme:"), parent=section
        )
        prev_lbl.setProperty("cssClass", "text-secondary")
        layout.addWidget(prev_lbl)

        self._font_preview = QLabel(
            "Hızlı kahverengi tilki — The quick brown fox 0123456789",
            parent=section,
        )
        self._font_preview.setProperty("cssClass", "text-primary")
        self._font_preview.setStyleSheet("padding: 10px; border-radius: 4px;")
        self._font_preview.setWordWrap(True)
        layout.addWidget(self._font_preview)

        apply_row = QHBoxLayout()
        apply_row.addStretch()
        self._font_apply_btn = QPushButton(
            tr("settings_font_apply", "Uygula"), parent=section
        )
        self._font_apply_btn.setProperty("cssClass", "btn-primary")
        self._font_apply_btn.setFixedHeight(Size.BTN_SM_H)
        self._font_apply_btn.clicked.connect(self._on_apply_font)
        apply_row.addWidget(self._font_apply_btn)
        layout.addLayout(apply_row)

        self._update_font_preview()

        self._font_combo.currentIndexChanged.connect(self._on_font_changed)
        self._font_size_spin.valueChanged.connect(self._on_font_size_changed)

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

    def _populate_theme_combo(self, combo: QComboBox, slot_key: str) -> None:
        combo.blockSignals(True)
        combo.clear()
        themes = self._theme.list_themes()
        saved_slot = (
            self._prefs.load_dark_slot()
            if slot_key == "dark"
            else self._prefs.load_light_slot()
        )
        select_idx = 0
        for i, t in enumerate(themes):
            suffix = " ★" if t["builtin"] else ""
            combo.addItem(t["name"] + suffix, t["name"])
            if t["name"] == saved_slot:
                select_idx = i
        combo.setCurrentIndex(select_idx)
        combo.blockSignals(False)

    def _populate_font_combo(self) -> None:
        self._font_combo.blockSignals(True)
        families = sorted(set(QFontDatabase.families()))
        saved = self._prefs.load_font_family()
        select_idx = 0
        for i, fam in enumerate(families):
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

    def _update_del_btn_state(self, btn: QPushButton, name: str) -> None:
        is_builtin = self._theme.is_builtin(name)
        btn.setEnabled(not is_builtin)
        btn.setToolTip("Yerleşik tema silinemez." if is_builtin else "")

    def _update_font_preview(self) -> None:
        family = self._font_combo.currentText()
        size = self._font_size_spin.value()
        font = QFont(family, size)
        self._font_preview.setFont(font)

    def _refresh_all_theme_combos(self) -> None:
        if hasattr(self, "_dark_combo"):
            self._populate_theme_combo(self._dark_combo, "dark")
        if hasattr(self, "_light_combo"):
            self._populate_theme_combo(self._light_combo, "light")

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

    def _on_slot_changed(self, slot_key: str, combo: QComboBox) -> None:
        name = combo.currentData()
        if not name:
            return
        if slot_key == "dark":
            self._prefs.save_dark_slot(name)
            # Eğer koyu mod aktifse temayı hemen uygula
            if self._prefs.load_active_mode() == "dark":
                self._prefs.save_theme(name)
                self._theme.switch_theme(name)
        else:
            self._prefs.save_light_slot(name)
            if self._prefs.load_active_mode() == "light":
                self._prefs.save_theme(name)
                self._theme.switch_theme(name)

    def _on_new_theme(self) -> None:
        dlg = ThemeEditorDialog(self._theme, theme_name=None, parent=self)
        dlg.theme_saved.connect(self._on_theme_editor_saved)
        dlg.exec()

    def _on_edit_theme(self, name: str | None) -> None:
        if not name:
            return
        dlg = ThemeEditorDialog(self._theme, theme_name=name, parent=self)
        dlg.theme_saved.connect(self._on_theme_editor_saved)
        dlg.exec()

    def _on_copy_theme(self, name: str | None, combo: QComboBox) -> None:
        if not name:
            return
        dest, ok = QInputDialog.getText(
            self,
            tr("settings_theme_copy_btn", "Kopyala"),
            "Yeni tema adı:",
            text=f"{name}_kopya",
        )
        if ok and dest.strip():
            dest = dest.strip()
            existing = [t["name"] for t in self._theme.list_themes()]
            if dest in existing:
                QMessageBox.warning(self, "Hata", "Bu isimde bir tema zaten mevcut.")
                return
            if self._theme.duplicate_theme(name, dest):
                self._refresh_all_theme_combos()

    def _on_export_theme(self, name: str | None) -> None:
        if not name:
            return
        content = self._theme.export_theme(name)
        if not content:
            QMessageBox.warning(self, "Hata", "Tema dosyası bulunamadı.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            tr("settings_theme_export_dialog", "Temayı Dışa Aktar"),
            f"{name}.json",
            tr("settings_theme_filter", "Tema Dosyası (*.json)"),
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                QMessageBox.information(
                    self, tr("success_title", "Başarılı"), f"Tema dışa aktarıldı:\n{path}"
                )
            except OSError as e:
                QMessageBox.warning(self, tr("error_title", "Hata"), str(e))

    def _on_delete_theme(
        self, name: str | None, slot_key: str, combo: QComboBox
    ) -> None:
        if not name or self._theme.is_builtin(name):
            return
        reply = QMessageBox.question(
            self,
            tr("settings_theme_delete_btn", "Sil"),
            tr(
                "settings_theme_delete_confirm",
                "Bu temayı silmek istediğinizden emin misiniz?",
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        # Slot resetle (silinecek tema slotta atanmışsa built-in'e döndür)
        if self._prefs.load_dark_slot() == name:
            self._prefs.save_dark_slot("dark")
        if self._prefs.load_light_slot() == name:
            self._prefs.save_light_slot("light")
        # Aktif tema siliniyorsa fallback
        active_mode = self._prefs.load_active_mode()
        current_slot = (
            self._prefs.load_dark_slot()
            if active_mode == "dark"
            else self._prefs.load_light_slot()
        )
        self._theme.delete_theme(name)
        self._refresh_all_theme_combos()
        # Eğer silinen tema aktifti, yeni slotu yükle
        if self._theme.current_theme == name:
            self._theme.switch_theme(current_slot)

    def _on_theme_editor_saved(self, name: str) -> None:
        self._refresh_all_theme_combos()

    def _on_import_theme(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            tr("settings_theme_import_dialog", "Tema İçe Aktar"),
            "",
            tr("settings_theme_filter", "Tema Dosyası (*.json)"),
        )
        if not path:
            return
        try:
            content = open(path, encoding="utf-8").read()
        except OSError as e:
            QMessageBox.warning(self, tr("error_title", "Hata"), str(e))
            return
        # İsim öner: dosya adı
        from pathlib import Path as _P
        suggested = _P(path).stem
        name, ok = QInputDialog.getText(
            self,
            tr("settings_theme_import_btn", "İçe Aktar"),
            "Tema adı:",
            text=suggested,
        )
        if not ok or not name.strip():
            return
        name = name.strip()
        existing = [t["name"] for t in self._theme.list_themes()]
        if name in existing:
            QMessageBox.warning(self, "Hata", "Bu isimde bir tema zaten mevcut.")
            return
        if self._theme.import_theme(content, name):
            self._refresh_all_theme_combos()
            QMessageBox.information(
                self, tr("success_title", "Başarılı"), f'"{name}" teması içe aktarıldı.'
            )
        else:
            QMessageBox.warning(self, tr("error_title", "Hata"), "Geçersiz tema dosyası.")

    def _on_accent_quick_change(self, hex_color: str) -> None:
        palette = dict(self._theme._palette)
        palette["accent_start"] = hex_color
        palette["accent_end"] = hex_color
        full = ThemeManager.derive_alpha_tokens(palette)
        self._theme.preview_palette(full)
        # Aktif temayı güncelle (kalıcı değil; sadece anlık uygulama)
        name = self._theme.current_theme
        if not self._theme.is_builtin(name):
            self._theme.update_theme(name, full)
            self._theme.restore_preview()
            self._theme.switch_theme(name)
        else:
            # Geçici uygula, kalıcı kaydetmeden çık
            self._theme.restore_preview()
            temp_name = f"{name}_vurgu_kopya"
            existing = [t["name"] for t in self._theme.list_themes()]
            if temp_name not in existing:
                self._theme.create_theme(temp_name, full)
            else:
                self._theme.update_theme(temp_name, full)
            self._theme.switch_theme(temp_name)
            active_mode = self._prefs.load_active_mode()
            if active_mode == "dark":
                self._prefs.save_dark_slot(temp_name)
            else:
                self._prefs.save_light_slot(temp_name)
            self._prefs.save_theme(temp_name)
            self._refresh_all_theme_combos()

    # ── Font İşleyicileri ────────────────────────────────────────────────────

    def _on_font_changed(self, _idx: int) -> None:
        self._update_font_preview()

    def _on_font_size_changed(self, _size: int) -> None:
        self._update_font_preview()

    def _on_apply_font(self) -> None:
        family = self._font_combo.currentText()
        size = self._font_size_spin.value()
        self._prefs.save_font_family(family)
        self._prefs.save_font_size(size)
        QApplication.instance().setFont(QFont(family, size))  # type: ignore[union-attr]

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
