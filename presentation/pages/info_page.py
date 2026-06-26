"""
Uygulama tanıtım ve kullanım rehberi sayfası.

Native PySide6 widget'larla oluşturulur; IconManager ile tema uyumlu
SVG ikonlar kullanır. Tema değişiminde _refresh_icons() ikon renklerini günceller.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

import config
from core.managers.icon_manager import IconManager, Icons
from core.managers.theme_manager import ThemeManager
from presentation.dimensions import FontFamily, Size, Spacing
from presentation.utils.i18n import tr

# (icon_name, title_key, title_default, desc_key, desc_default)
_FEATURES: list[tuple[str, str, str, str, str]] = [
    (
        Icons.HOUSE,
        "nav_dashboard", "Dashboard",
        "info_feat_dashboard_desc",
        "Proje sayısı, bekleyen ve tamamlanan görevler. Tıkanan projeler ile acil işler tek bakışta.",
    ),
    (
        Icons.FOLDER,
        "nav_projects", "Projeler",
        "info_feat_projects_desc",
        "Aşama aşama takip: Planlandı → Geliştirme → Test → Tamamlandı. Kararlar, notlar, kaynak bağlantıları.",
    ),
    (
        Icons.LIGHTBULB,
        "nav_ideas", "Fikirler",
        "info_feat_ideas_desc",
        "Ham fikirleri kaydedin, puanlayın. 'Projeye Dönüştür' ile veri kaybetmeden doğrudan projeye aktarın.",
    ),
    (
        Icons.SQUARE_CHECK,
        "nav_tasks", "Görevler",
        "info_feat_tasks_desc",
        "Hiyerarşik iş kırılımı (WBS). Durum, öncelik ve tür filtreleriyle görev yoğunluğunu kontrol edin.",
    ),
]

# (keys_display, desc_key, desc_default)
_SHORTCUTS: list[tuple[str, str, str]] = [
    ("Ctrl+F  /  Ctrl+K", "info_shortcut_search", "Hızlı Arama kutusunu açar"),
    ("Ctrl+N",            "info_shortcut_new",    "Yeni Proje oluşturur"),
]


class InfoPage(QWidget):
    """Uygulama tanıtım ve kullanım kılavuzu sayfası."""

    def __init__(
        self,
        parent: QWidget | None = None,
        theme: ThemeManager | None = None,
        icons: IconManager | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self._theme = theme or ThemeManager.instance()
        self._icons = icons or IconManager.instance()
        # (label, icon_name, color_key, px_size) — tema değişiminde yenilenir
        self._icon_refs: list[tuple[QLabel, str, str, int]] = []
        self._setup_ui()
        self._theme.theme_changed.connect(self._refresh_icons)

    # ── Kuruluş ──────────────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        outer.addWidget(self._build_header())

        divider = QFrame(parent=self)
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setProperty("cssClass", "divider")
        divider.setFixedHeight(Size.SIDEBAR_DIVIDER_H)
        outer.addWidget(divider)

        scroll = QScrollArea(parent=self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        page = QWidget(parent=scroll)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(Spacing.PAGE, Spacing.PAGE, Spacing.PAGE, Spacing.PAGE)
        layout.setSpacing(Spacing.XXXL)

        layout.addWidget(self._build_hero(page))
        layout.addWidget(self._hline(page))
        layout.addWidget(self._build_workflow_section(page))
        layout.addWidget(self._hline(page))
        layout.addWidget(self._build_features_section(page))
        layout.addWidget(self._hline(page))
        layout.addWidget(self._build_tips_section(page))
        layout.addWidget(self._hline(page))
        layout.addWidget(self._build_shortcuts_section(page))
        layout.addWidget(self._build_footer(page))
        layout.addStretch()

        scroll.setWidget(page)
        outer.addWidget(scroll)

    def _build_header(self) -> QWidget:
        header = QWidget(parent=self)
        header.setFixedHeight(Size.PAGE_HEADER_H)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(Spacing.PAGE, 0, Spacing.PAGE, 0)
        title = QLabel(tr("info_title", "Bilgilendirme ve Kullanım Rehberi"), parent=header)
        title.setProperty("cssClass", "title-large")
        hl.addWidget(title)
        return header

    # ── Hero bölümü ──────────────────────────────────────────────────────────

    def _build_hero(self, parent: QWidget) -> QFrame:
        hero = QFrame(parent=parent)
        hero.setProperty("cssClass", "panel")
        layout = QVBoxLayout(hero)
        layout.setContentsMargins(Spacing.XXXL, Spacing.XXXL, Spacing.XXXL, Spacing.XXXL)
        layout.setSpacing(Spacing.SM)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        icon_lbl = self._icon_label(Icons.CIRCLE_INFO, "accent_start", 48, parent=hero)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_lbl)

        name_lbl = QLabel(config.APP_NAME, parent=hero)
        name_lbl.setProperty("cssClass", "title-large")
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_lbl)

        ver_lbl = QLabel(f"v{config.APP_VERSION}", parent=hero)
        ver_lbl.setProperty("cssClass", "text-muted")
        ver_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(ver_lbl)

        tag_lbl = QLabel(
            tr(
                "info_tagline",
                "Yazılım projelerinizi, fikirlerinizi ve görevlerinizi tek merkezden yönetin.",
            ),
            parent=hero,
        )
        tag_lbl.setProperty("cssClass", "text-secondary")
        tag_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tag_lbl.setWordWrap(True)
        layout.addWidget(tag_lbl)

        return hero

    # ── Çalışma akışı ────────────────────────────────────────────────────────

    def _build_workflow_section(self, parent: QWidget) -> QWidget:
        section = QWidget(parent=parent)
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.LG)

        title = QLabel(tr("info_workflow_title", "Çalışma Akışı"), parent=section)
        title.setProperty("cssClass", "title-small")
        layout.addWidget(title)

        flow_row = QHBoxLayout()
        flow_row.setSpacing(0)

        nodes = [
            (Icons.LIGHTBULB,    "info_flow_ideas",    "Fikir Havuzu"),
            (Icons.FOLDER,       "info_flow_projects", "Projeler"),
            (Icons.SQUARE_CHECK, "info_flow_tasks",    "Görevler (WBS)"),
        ]
        for i, (icon_name, label_key, label_default) in enumerate(nodes):
            node = QFrame(parent=section)
            node.setProperty("cssClass", "panel")
            nl = QVBoxLayout(node)
            nl.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
            nl.setSpacing(Spacing.SM)
            nl.setAlignment(Qt.AlignmentFlag.AlignCenter)

            icon_lbl = self._icon_label(icon_name, "accent_start", 28, parent=node)
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            nl.addWidget(icon_lbl)

            lbl = QLabel(tr(label_key, label_default), parent=node)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setProperty("cssClass", "text-primary")
            lbl.setStyleSheet("font-weight: 700;")
            nl.addWidget(lbl)

            flow_row.addWidget(node, 3)

            if i < len(nodes) - 1:
                arrow = QLabel("→", parent=section)
                arrow.setAlignment(Qt.AlignmentFlag.AlignCenter)
                arrow.setProperty("cssClass", "text-secondary")
                arrow.setStyleSheet("font-size: 20px; font-weight: 700;")
                flow_row.addWidget(arrow, 1)

        layout.addLayout(flow_row)
        return section

    # ── Özellik kartları ─────────────────────────────────────────────────────

    def _build_features_section(self, parent: QWidget) -> QWidget:
        section = QWidget(parent=parent)
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.LG)

        title = QLabel(tr("info_features_title", "Sistem Bileşenleri"), parent=section)
        title.setProperty("cssClass", "title-small")
        layout.addWidget(title)

        for row_start in range(0, len(_FEATURES), 2):
            row_layout = QHBoxLayout()
            row_layout.setSpacing(Spacing.LG)
            for feat in _FEATURES[row_start : row_start + 2]:
                row_layout.addWidget(self._build_feature_card(feat, section), 1)
            layout.addLayout(row_layout)

        return section

    def _build_feature_card(
        self,
        feat: tuple[str, str, str, str, str],
        parent: QWidget,
    ) -> QFrame:
        icon_name, title_key, title_default, desc_key, desc_default = feat
        card = QFrame(parent=parent)
        card.setProperty("cssClass", "panel")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        cl.setSpacing(Spacing.SM)

        top = QHBoxLayout()
        top.setSpacing(Spacing.SM)
        icon_lbl = self._icon_label(icon_name, "accent_start", 22, parent=card)
        top.addWidget(icon_lbl)
        title_lbl = QLabel(tr(title_key, title_default), parent=card)
        title_lbl.setProperty("cssClass", "text-primary")
        title_lbl.setStyleSheet("font-weight: 700;")
        top.addWidget(title_lbl, 1)
        cl.addLayout(top)

        desc_lbl = QLabel(tr(desc_key, desc_default), parent=card)
        desc_lbl.setProperty("cssClass", "text-secondary")
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("font-size: 12px;")
        cl.addWidget(desc_lbl)

        return card

    # ── İpuçları ─────────────────────────────────────────────────────────────

    def _build_tips_section(self, parent: QWidget) -> QWidget:
        section = QWidget(parent=parent)
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.LG)

        title = QLabel(tr("info_tips_title", "Önemli İpuçları"), parent=section)
        title.setProperty("cssClass", "title-small")
        layout.addWidget(title)

        tips = [
            (Icons.SETTINGS, "accent_start",
             tr("info_tip_theme_title", "Dinamik Tema Desteği"),
             tr("info_tip_theme_desc",
                "Sol menünün en altındaki toggle ile Koyu/Açık modlar arasında anlık geçiş yapın. "
                "Ayarlar → Tema bölümünden özel renk temaları oluşturabilirsiniz.")),
            (Icons.ARCHIVE, "success",
             tr("info_tip_data_title", "Yerel Veri Depolama"),
             tr("info_tip_data_desc",
                "Tüm veriler SQLite veritabanı olarak yerel sisteminizde tutulur. "
                "Ayarlar → Veri Yönetimi'nden JSON formatında dışa aktarabilirsiniz.")),
        ]
        for icon_name, color_key, tip_title, tip_desc in tips:
            card = QFrame(parent=section)
            card.setProperty("cssClass", "panel")
            cl = QHBoxLayout(card)
            cl.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
            cl.setSpacing(Spacing.MD)

            icon_lbl = self._icon_label(icon_name, color_key, 24, parent=card)
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
            cl.addWidget(icon_lbl)

            tl = QVBoxLayout()
            tl.setSpacing(Spacing.XS)
            title_lbl = QLabel(tip_title, parent=card)
            title_lbl.setProperty("cssClass", "text-primary")
            title_lbl.setStyleSheet("font-weight: 700;")
            tl.addWidget(title_lbl)
            desc_lbl = QLabel(tip_desc, parent=card)
            desc_lbl.setProperty("cssClass", "text-secondary")
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet("font-size: 12px;")
            tl.addWidget(desc_lbl)
            cl.addLayout(tl, 1)

            layout.addWidget(card)

        return section

    # ── Kısayollar ───────────────────────────────────────────────────────────

    def _build_shortcuts_section(self, parent: QWidget) -> QWidget:
        section = QWidget(parent=parent)
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.LG)

        title = QLabel(tr("info_shortcuts_title", "Klavye Kısayolları"), parent=section)
        title.setProperty("cssClass", "title-small")
        layout.addWidget(title)

        panel = QFrame(parent=section)
        panel.setProperty("cssClass", "panel")
        pl = QVBoxLayout(panel)
        pl.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        pl.setSpacing(Spacing.MD)

        for keys_str, desc_key, desc_default in _SHORTCUTS:
            row = QHBoxLayout()
            row.setSpacing(Spacing.MD)

            kbd = QLabel(keys_str, parent=panel)
            kbd.setProperty("cssClass", "text-primary")
            kbd.setStyleSheet(
                f"font-family: '{FontFamily.MONO}', {FontFamily.FALLBACK_MONO};"
                " font-weight: 700; font-size: 12px;"
            )
            kbd.setFixedWidth(170)
            row.addWidget(kbd)

            sep = QFrame(parent=panel)
            sep.setFrameShape(QFrame.Shape.VLine)
            sep.setProperty("cssClass", "divider")
            sep.setFixedWidth(1)
            row.addWidget(sep)

            desc = QLabel(tr(desc_key, desc_default), parent=panel)
            desc.setProperty("cssClass", "text-secondary")
            row.addWidget(desc, 1)

            pl.addLayout(row)

        layout.addWidget(panel)
        return section

    # ── Alt bilgi ────────────────────────────────────────────────────────────

    def _build_footer(self, parent: QWidget) -> QLabel:
        footer = QLabel(
            f"{config.APP_NAME}  ·  v{config.APP_VERSION}",
            parent=parent,
        )
        footer.setProperty("cssClass", "text-muted")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("padding: 8px 0; font-size: 11px;")
        return footer

    # ── Yardımcılar ──────────────────────────────────────────────────────────

    def _icon_label(
        self, icon_name: str, color_key: str, size: int, parent: QWidget
    ) -> QLabel:
        lbl = QLabel(parent=parent)
        icon = self._icons.get_icon(icon_name, self._theme.color(color_key))
        lbl.setPixmap(icon.pixmap(size, size))
        self._icon_refs.append((lbl, icon_name, color_key, size))
        return lbl

    def _hline(self, parent: QWidget) -> QFrame:
        line = QFrame(parent=parent)
        line.setFrameShape(QFrame.Shape.HLine)
        line.setProperty("cssClass", "divider")
        line.setFixedHeight(1)
        return line

    def _refresh_icons(self) -> None:
        for lbl, icon_name, color_key, size in self._icon_refs:
            icon = self._icons.get_icon(icon_name, self._theme.color(color_key))
            lbl.setPixmap(icon.pixmap(size, size))
