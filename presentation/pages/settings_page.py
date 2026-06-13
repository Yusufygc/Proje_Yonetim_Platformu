"""
Ayarlar sayfası — tema, tercihler, dışa aktarma (export) ve yedekleme (backup) işlemleri.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import config
from controllers.settings_controller import SettingsController
from core.managers.preference_manager import PreferenceManager
from core.managers.string_manager import StringManager
from presentation.dimensions import Size, Spacing
from presentation.utils.i18n import tr

# Desteklenen diller: (görünen ad, dil kodu). Görünen ad kendi dilinde
# yazılır — kullanıcı mevcut dili bilmese de kendi dilini tanır.
_LANGUAGES: list[tuple[str, str]] = [
    ("Türkçe", "tr"),  # l10n: data — dil adı kendi dilinde sabittir
    ("English", "en"),
]


class SettingsPage(QWidget):
    """Uygulama ayarlarının ve veri yönetiminin yapıldığı sayfa."""

    def __init__(
        self,
        parent: QWidget,
        controller: SettingsController,
        strings: StringManager | None = None,
        prefs: PreferenceManager | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self._controller = controller
        # Constructor injection tercih edilir; None ise singleton'a düşülür.
        self._strings = strings or StringManager.instance()
        self._prefs = prefs or PreferenceManager.instance()
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.PAGE, Spacing.PAGE, Spacing.PAGE, Spacing.PAGE)
        layout.setSpacing(Spacing.XXXL)

        # Header
        title = QLabel(tr("settings_title", "Ayarlar ve Veri Yönetimi"), parent=self)
        title.setProperty("cssClass", "title-large")
        layout.addWidget(title)

        # Data Management Section
        data_lbl = QLabel(tr("settings_data_section", "Veri Yönetimi"), parent=self)
        data_lbl.setProperty("cssClass", "title-small")
        layout.addWidget(data_lbl)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(Spacing.XL)
        
        self._btn_backup = QPushButton(tr("settings_backup_btn", "💾 Veritabanını Yedekle (.db)"), parent=self)
        self._btn_backup.setProperty("cssClass", "btn-secondary")
        self._btn_backup.clicked.connect(self._on_backup_clicked)
        btn_layout.addWidget(self._btn_backup)

        self._btn_export = QPushButton(tr("settings_export_btn", "📤 Tüm Veriyi Dışa Aktar (.json)"), parent=self)
        self._btn_export.setProperty("cssClass", "btn-primary")
        self._btn_export.clicked.connect(self._on_export_clicked)
        btn_layout.addWidget(self._btn_export)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        layout.addWidget(self._build_language_section())

        layout.addStretch()

        # Footer
        version_label = QLabel(
            f"{config.APP_NAME}  —  v{config.APP_VERSION}", parent=self
        )
        version_label.setProperty("cssClass", "text-secondary")
        layout.addWidget(version_label)

    def _build_language_section(self) -> QWidget:
        section = QWidget(parent=self)
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.LG)

        lang_lbl = QLabel(tr("settings_language_section", "Dil"), parent=section)
        lang_lbl.setProperty("cssClass", "title-small")
        layout.addWidget(lang_lbl)

        row = QHBoxLayout()
        row.setSpacing(Spacing.XL)
        self._language_combo = QComboBox(parent=section)
        self._language_combo.setMinimumHeight(Size.BTN_SM_H)
        self._language_combo.setMinimumWidth(180)
        current = self._strings.current_language
        for label, code in _LANGUAGES:
            self._language_combo.addItem(label, code)
        idx = self._language_combo.findData(current)
        if idx >= 0:
            self._language_combo.setCurrentIndex(idx)
        self._language_combo.currentIndexChanged.connect(self._on_language_changed)
        row.addWidget(self._language_combo)
        row.addStretch()
        layout.addLayout(row)

        return section

    def _on_language_changed(self, index: int) -> None:
        lang_code = self._language_combo.itemData(index)
        if not lang_code or lang_code == self._strings.current_language:
            return
        self._prefs.save_language(lang_code)
        self._strings.set_language(lang_code)
        # Statik metin kuran sayfalar yeniden kurulmadan eski dilde kalır;
        # tam geçiş yeniden başlatmayla garanti edilir.
        QMessageBox.information(
            self,
            tr("settings_language_section", "Dil"),
            tr(
                "settings_language_restart",
                "Dil tercihi kaydedildi. Değişikliğin tüm ekranlara uygulanması için uygulamayı yeniden başlatın.",
            ),
        )

    def _connect_signals(self) -> None:
        self._controller.backup_completed.connect(self._on_backup_completed)
        self._controller.export_completed.connect(self._on_export_completed)
        self._controller.error_occurred.connect(self._on_error)

    def _on_backup_clicked(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            tr("settings_backup_dialog_title", "Veritabanını Yedekle"),
            "proje_takip_yedek.db",
            tr("settings_backup_filter", "SQLite Veritabanı (*.db)"),
        )
        if path:
            self._controller.backup_database(path)

    def _on_export_clicked(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            tr("settings_export_dialog_title", "Veriyi Dışa Aktar"),
            "proje_takip_export.json",
            tr("settings_export_filter", "JSON Dosyası (*.json)"),
        )
        if path:
            self._controller.export_to_json(path)

    def _on_backup_completed(self, path: str) -> None:
        QMessageBox.information(
            self,
            tr("success_title", "Başarılı"),
            tr("settings_backup_done", "Veritabanı başarıyla yedeklendi:\n{path}").format(path=path),
        )

    def _on_export_completed(self, path: str) -> None:
        QMessageBox.information(
            self,
            tr("success_title", "Başarılı"),
            tr("settings_export_done", "Veriler başarıyla dışa aktarıldı:\n{path}").format(path=path),
        )

    def _on_error(self, message: str) -> None:
        QMessageBox.warning(self, tr("error_title", "Hata"), message)
