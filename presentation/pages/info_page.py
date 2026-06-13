"""
Uygulama kullanım rehberini içeren bilgilendirme sayfası.

İçerik/sunum/stil ayrımı:
  - HTML içerik → resources/templates/info_page.html
  - Belge stili → resources/styles/pages/info_browser.css  (token çözümlü)
  - Widget yapısı → bu dosya

Tema değiştiğinde CSS token'ları yeniden çözümlenerek browser güncellenir.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

import config
from core.managers.theme_manager import ThemeManager
from presentation.dimensions import Size, Spacing
from presentation.utils.i18n import tr


class InfoPage(QWidget):
    """Uygulamanın nasıl kullanılacağını anlatan statik bilgilendirme sayfası."""

    def __init__(self, parent: QWidget | None = None, theme: ThemeManager | None = None) -> None:
        super().__init__(parent=parent)
        # Constructor injection tercih edilir; None ise singleton'a düşülür.
        self._theme = theme or ThemeManager.instance()
        self._setup_ui()
        # Tema değişiminde CSS token'larını yenile
        self._theme.theme_changed.connect(self._apply_browser_style)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._build_header())

        divider = QFrame(parent=self)
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setProperty("cssClass", "divider")
        divider.setFixedHeight(Size.SIDEBAR_DIVIDER_H)
        layout.addWidget(divider)

        self._browser = QTextBrowser(parent=self)
        self._browser.setObjectName("info_browser")
        self._browser.setOpenExternalLinks(True)
        self._browser.setFrameShape(QFrame.Shape.NoFrame)
        self._apply_browser_style()
        layout.addWidget(self._browser)

    def _build_header(self) -> QWidget:
        header = QWidget(parent=self)
        header.setFixedHeight(Size.PAGE_HEADER_H)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(Spacing.PAGE, 0, Spacing.PAGE, 0)

        title = QLabel(tr("info_title", "Bilgilendirme ve Kullanım Rehberi"), parent=header)
        title.setProperty("cssClass", "title-large")
        header_layout.addWidget(title)
        return header

    def _apply_browser_style(self) -> None:
        """CSS token'larını aktif temaya göre çözümler ve browser'a uygular."""
        css_file = config.STYLES_DIR / "pages" / "info_browser.css"
        html_file = config.RESOURCES_DIR / "templates" / "info_page.html"

        try:
            raw_css = css_file.read_text(encoding="utf-8")
            html = html_file.read_text(encoding="utf-8")
        except OSError:
            return

        resolved_css = self._theme.resolve_tokens(raw_css)
        self._browser.document().setDefaultStyleSheet(resolved_css)
        self._browser.setHtml(html)
