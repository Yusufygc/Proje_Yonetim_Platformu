"""
Ayarlar sayfası — tema, tercihler, dışa aktarma (export) ve yedekleme (backup) işlemleri.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
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


class SettingsPage(QWidget):
    """Uygulama ayarlarının ve veri yönetiminin yapıldığı sayfa."""

    def __init__(self, parent: QWidget, controller: SettingsController) -> None:
        super().__init__(parent=parent)
        self._controller = controller
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # Header
        title = QLabel("Ayarlar ve Veri Yönetimi", parent=self)
        title.setStyleSheet("font-size: 26px; font-weight: 800; color: #FFFFFF;")
        layout.addWidget(title)

        # Data Management Section
        data_lbl = QLabel("Veri Yönetimi", parent=self)
        data_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #E8EAF0;")
        layout.addWidget(data_lbl)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(16)
        
        self._btn_backup = QPushButton("💾 Veritabanını Yedekle (.db)", parent=self)
        self._btn_backup.setStyleSheet("""
            QPushButton {
                background-color: #3B3E4D; color: white; border-radius: 8px; padding: 12px 24px; font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { background-color: #4A4D5C; }
        """)
        self._btn_backup.clicked.connect(self._on_backup_clicked)
        btn_layout.addWidget(self._btn_backup)

        self._btn_export = QPushButton("📤 Tüm Veriyi Dışa Aktar (.json)", parent=self)
        self._btn_export.setStyleSheet("""
            QPushButton {
                background-color: #6366F1; color: white; border-radius: 8px; padding: 12px 24px; font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { background-color: #8B5CF6; }
        """)
        self._btn_export.clicked.connect(self._on_export_clicked)
        btn_layout.addWidget(self._btn_export)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        layout.addStretch()

        # Footer
        version_label = QLabel(
            f"{config.APP_NAME}  —  v{config.APP_VERSION}", parent=self
        )
        version_label.setStyleSheet("font-size: 13px; color: #8B8FA8;")
        layout.addWidget(version_label)

    def _connect_signals(self) -> None:
        self._controller.backup_completed.connect(self._on_backup_completed)
        self._controller.export_completed.connect(self._on_export_completed)
        self._controller.error_occurred.connect(self._on_error)

    def _on_backup_clicked(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Veritabanını Yedekle", "proje_takip_yedek.db", "SQLite Veritabanı (*.db)"
        )
        if path:
            self._controller.backup_database(path)

    def _on_export_clicked(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Veriyi Dışa Aktar", "proje_takip_export.json", "JSON Dosyası (*.json)"
        )
        if path:
            self._controller.export_to_json(path)

    def _on_backup_completed(self, path: str) -> None:
        QMessageBox.information(self, "Başarılı", f"Veritabanı başarıyla yedeklendi:\n{path}")

    def _on_export_completed(self, path: str) -> None:
        QMessageBox.information(self, "Başarılı", f"Veriler başarıyla dışa aktarıldı:\n{path}")

    def _on_error(self, message: str) -> None:
        QMessageBox.warning(self, "Hata", message)
