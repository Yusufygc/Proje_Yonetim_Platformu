"""
Arşiv sayfası — arşivlenen projeleri listeler.
Her proje için geri alma (arşivden çıkar) ve kalıcı silme seçenekleri sunar.
"""
from __future__ import annotations

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from controllers.project_controller import ProjectController
from core.managers.icon_manager import IconManager, Icons
from core.managers.theme_manager import ThemeManager
from domain.models.project import Project
from presentation.dimensions import Spacing
from presentation.utils.i18n import tr

_STATUS_LABELS: dict[str, str] = {
    "PLANNED": "Planlandı",
    "ACTIVE": "Aktif",
    "ON_HOLD": "Beklemede",
    "BLOCKED": "Engellendi",
    "COMPLETED": "Tamamlandı",
    "CANCELLED": "İptal Edildi",
    "ARCHIVED": "Arşivlendi",
}


class _TrashButton(QPushButton):
    """Hover'da kırmızı zemin + beyaz ikon; enter/leave ile ikon rengi değiştirilir."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self._icons = IconManager.try_instance()
        self._theme = ThemeManager.instance()
        self.setFixedSize(30, 30)
        self.setIconSize(QSize(16, 16))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(tr("action_delete", "Kalıcı Sil"))
        self.setStyleSheet(
            "QPushButton { background: transparent; border: none; border-radius: 6px; padding: 0; }"
            " QPushButton:hover { background-color: #e53935; }"
        )
        self._set_icon(hover=False)

    def _set_icon(self, hover: bool) -> None:
        if self._icons:
            color = "#FFFFFF" if hover else self._theme.color("text_muted")
            self.setIcon(self._icons.get_icon(Icons.TRASH, color))

    def enterEvent(self, event: object) -> None:
        self._set_icon(hover=True)
        super().enterEvent(event)

    def leaveEvent(self, event: object) -> None:
        self._set_icon(hover=False)
        super().leaveEvent(event)


class _ArchiveRow(QFrame):
    """Arşivlenmiş proje satırı: başlık, durum etiketi, geri al ve sil butonları."""

    restore_requested = Signal(int)
    delete_requested = Signal(int)

    def __init__(self, project: Project, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self._project_id = project.id
        self.setProperty("cssClass", "panel")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(Spacing.XL, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.MD)

        title_lbl = QLabel(project.title, parent=self)
        title_lbl.setProperty("cssClass", "text-primary")
        title_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(title_lbl, 1)

        status_text = _STATUS_LABELS.get(project.status, project.status)
        status_lbl = QLabel(status_text, parent=self)
        status_lbl.setProperty("cssClass", "text-muted")
        status_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(status_lbl)

        restore_btn = QPushButton(tr("action_restore", "Geri Al"), parent=self)
        restore_btn.setFixedHeight(30)
        restore_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        restore_btn.setProperty("cssClass", "btn-secondary")
        restore_btn.clicked.connect(lambda: self.restore_requested.emit(self._project_id))
        layout.addWidget(restore_btn)

        del_btn = _TrashButton(parent=self)
        del_btn.clicked.connect(lambda: self.delete_requested.emit(self._project_id))
        layout.addWidget(del_btn)


class ArchivePage(QWidget):
    """Arşivlenen projelerin listelendiği ve yönetildiği sayfa."""

    def __init__(
        self,
        parent: QWidget,
        controller: ProjectController,
    ) -> None:
        super().__init__(parent=parent)
        self._controller = controller
        self._rows: dict[int, _ArchiveRow] = {}
        self._setup_ui()
        self._connect_signals()
        self._controller.load_archived_projects()

    def _setup_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(Spacing.PAGE, Spacing.PAGE, Spacing.PAGE, Spacing.PAGE)
        outer.setSpacing(Spacing.XL)

        # Başlık satırı
        header = QWidget(parent=self)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel(tr("nav_archive", "Arşiv"), parent=header)
        title.setProperty("cssClass", "title-medium")
        header_layout.addWidget(title)
        header_layout.addStretch()

        self._count_lbl = QLabel("", parent=header)
        self._count_lbl.setProperty("cssClass", "text-muted")
        header_layout.addWidget(self._count_lbl)
        outer.addWidget(header)

        # Boş durum
        self._empty_lbl = QLabel(
            tr("archive_empty", "Arşivlenmiş proje yok."),
            parent=self,
        )
        self._empty_lbl.setProperty("cssClass", "text-secondary")
        self._empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_lbl.hide()
        outer.addWidget(self._empty_lbl)

        # Kaydırılabilir liste
        scroll = QScrollArea(parent=self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # Scroll alanı arka planı şeffaf — tema rengi alttan görünsün
        scroll.setAutoFillBackground(False)
        scroll.viewport().setAutoFillBackground(False)

        self._list_widget = QWidget(parent=scroll)
        self._list_widget.setProperty("cssClass", "transparent-bg")
        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(Spacing.MD)
        self._list_layout.addStretch()

        scroll.setWidget(self._list_widget)
        outer.addWidget(scroll, 1)

    def _connect_signals(self) -> None:
        self._controller.archived_projects_loaded.connect(self._on_projects_loaded)
        self._controller.project_restored.connect(self._on_project_changed)
        self._controller.project_deleted.connect(self._on_project_changed)
        self._controller.error_occurred.connect(self._on_error)

    def _on_projects_loaded(self, projects: list[Project]) -> None:
        self._clear_rows()
        if not projects:
            self._empty_lbl.show()
            self._count_lbl.setText("")
        else:
            self._empty_lbl.hide()
            count = len(projects)
            self._count_lbl.setText(
                tr("archive_count", "{n} proje").format(n=count)
            )
            # Stretch en sona kalması için insertWidget kullanılır
            for project in projects:
                row = _ArchiveRow(project, parent=self._list_widget)
                row.restore_requested.connect(self._on_restore)
                row.delete_requested.connect(self._on_delete_confirm)
                insert_pos = self._list_layout.count() - 1
                self._list_layout.insertWidget(insert_pos, row)
                self._rows[project.id] = row

    def _clear_rows(self) -> None:
        for row in self._rows.values():
            self._list_layout.removeWidget(row)
            row.deleteLater()
        self._rows.clear()

    def _on_restore(self, project_id: int) -> None:
        self._controller.restore_archived_project(project_id)

    def _on_delete_confirm(self, project_id: int) -> None:
        row = self._rows.get(project_id)
        title = row._project_id if row is None else ""
        # Başlık için satırdan title label okuyamayız; genel mesaj yeterli.
        reply = QMessageBox.question(
            self,
            tr("archive_delete_title", "Kalıcı Sil"),
            tr(
                "archive_delete_confirm",
                "Bu proje ve tüm verisi kalıcı olarak silinecek. Geri alınamaz. Emin misiniz?",
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._controller.delete_project(project_id)

    def _on_project_changed(self, _id: int) -> None:
        self._controller.load_archived_projects()

    def _on_error(self, msg: str) -> None:
        QMessageBox.critical(self, tr("error_title", "Hata"), msg)

    def showEvent(self, event: object) -> None:
        # Sayfaya her geçişte listeyi tazele
        self._controller.load_archived_projects()
        super().showEvent(event)  # type: ignore[arg-type]
