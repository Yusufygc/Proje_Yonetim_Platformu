"""Sahne eylemleri. Anahtarlar `scenario.yaml` içindeki sahne kimlikleriyle aynıdır.

Her sahne tek başına çekilebilir: temiz örnek veriyle ana panelden başlar. Eylemin sonucu
`expect` ile doğrulanır; boşa giden bir tıklama videoya girmez, çekim durur.
"""
from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from driver import Driver, expect, scene_rect
from PySide6.QtCore import QPointF, Qt
from PySide6.QtQuick import QQuickItem
from seed import CHECKLIST_TASK, FEATURED_IDEA, FEATURED_PROJECT, MEMO_TITLE

logger = logging.getLogger("demo.capture")
SIDEBAR_RIGHT = 240
CHECKBOX_OFFSET = 17
CHEVRON_OFFSET = 44
Scene = Callable[[Driver, Any], None]


def _menu(driver: Driver, label: str) -> None:
    driver.click(driver.find(label, lambda r: r.right() <= SIDEBAR_RIGHT))
    driver.recorder.hold(0.5)


def _content(driver: Driver, text: str) -> QQuickItem:
    """Kenar çubuğu dışındaki ilk (en üstteki) eşleşme."""
    found = driver.matches(text, lambda r: r.left() > SIDEBAR_RIGHT)
    expect(bool(found), f"'{text}' içerik alanında yok")
    return found[0]


def ana_panel(driver: Driver, app: Any) -> None:
    driver.recorder.hold(1.2)
    cards = [driver.find("Aktif Projeler"), driver.find("Havuzdaki Fikirler")]
    driver.focus(*cards)
    driver.move(driver.center(driver.find("Açık Görevler")), 0.9)
    driver.recorder.hold(1.2)
    driver.say()
    header = driver.find("Yüksek Öncelikli Açık Görevler")
    last = driver.find("Para transferi formu doğrulaması")
    driver.focus(header, last)
    driver.move(driver.center(last), 0.9)
    driver.recorder.hold(1.4)
    driver.unfocus()
    driver.recorder.hold(1.0)


def fikir_proje(driver: Driver, app: Any) -> None:
    driver.recorder.hold(0.4)
    _menu(driver, "Fikirler")
    # Aynı başlık hem listede hem detayda görünebilir; listedeki soldakidir.
    card = min(driver.matches(FEATURED_IDEA), key=lambda i: scene_rect(i).x())
    driver.click(card)
    driver.recorder.hold(0.6)
    button = driver.find("Projeye Dönüştür")
    driver.say()
    driver.focus(button)
    driver.recorder.hold(0.6)
    driver.click(button)
    # Sonuç bildirimi pencerenin üstünde çıkar; kamera hemen geri çekilir.
    driver.unfocus()
    driver.recorder.hold(1.4)
    expect(not driver.matches("Projeye Dönüştür"), "fikir projeye dönüşmedi")
    driver.dismiss_toast()
    _menu(driver, "Projeler")
    driver.click(_content(driver, FEATURED_IDEA))
    driver.recorder.hold(0.4)
    problem = driver.find("Kullanıcılar harcamalarını elle etiketliyor.")
    driver.say()
    driver.focus(problem)
    driver.recorder.hold(1.8)
    driver.unfocus()
    driver.recorder.hold(0.8)


def asamalar(driver: Driver, app: Any) -> None:
    _menu(driver, "Projeler")
    driver.click(_content(driver, FEATURED_PROJECT))
    driver.recorder.hold(0.5)
    driver.focus(driver.find("1. Fikir"), driver.find("4. Geliştirme"), driver.matches("Tamamla")[0])
    driver.recorder.hold(0.6)
    driver.say()
    for expected_done in (1, 2):
        # En üstteki "Tamamla" düğmesi etkin aşamanındır; tamamlanınca satırdan kalkar.
        driver.click(driver.matches("Tamamla")[0])
        driver.recorder.hold(0.6)
        stages = app._project_viewmodel.selectedStages
        expect(sum(s["status"] == "DONE" for s in stages) == expected_done, "aşama tamamlanmadı")
    driver.unfocus()
    driver.recorder.hold(1.2)


def _open_featured_tasks(driver: Driver, app: Any) -> None:
    _menu(driver, "Görevler")
    wanted = next(p for p in app._task_viewmodel.projects if FEATURED_PROJECT in p.values())
    if app._task_viewmodel.selectedProjectId != wanted["id"]:
        app._task_viewmodel.selectProject(wanted["id"])
        driver.recorder.settle()
    driver.recorder.hold(0.4)


def _row_control(driver: Driver, title: str, offset: int) -> QPointF:
    """Onay kutusu ve açma oku metinsizdir; satırdaki sıra numarasının `offset` piksel solundadır."""
    row = scene_rect(_content(driver, title))
    codes = [
        scene_rect(i) for i in driver.items()
        if str(i.property("text") or "").replace(".", "").isdigit()
        and abs(scene_rect(i).center().y() - row.center().y()) < 8
        and SIDEBAR_RIGHT < scene_rect(i).right() <= row.left()
    ]
    expect(len(codes) == 1, f"'{title}' satırında sıra numarası bulunamadı")
    return QPointF(codes[0].left() - offset, row.center().y())


def gorev_agaci(driver: Driver, app: Any) -> None:
    _open_featured_tasks(driver, app)
    total = app._task_viewmodel.totalTasks
    # İlk grup kapatılır ki eklenen ve işaretlenen görevler listenin içinde kalsın.
    driver.click(_row_control(driver, "Analiz ve tasarım", CHEVRON_OFFSET))
    driver.click(_content(driver, "Geliştirme"))
    driver.say()
    field = driver.find("Seçili görevin altına hızlı görev ekle...")
    driver.focus(field, driver.find("Hızlı Ekle"))
    driver.click(field)
    driver.type_text("Giriş ekranı testleri")
    driver.recorder.hold(0.3)
    driver.click(driver.find("Hızlı Ekle"))
    driver.unfocus()
    driver.recorder.hold(1.0)
    expect(app._task_viewmodel.totalTasks == total + 1, "görev eklenmedi")
    expect(bool(driver.matches("Giriş ekranı testleri")), "eklenen görevin adı listede yok")
    driver.dismiss_toast()
    done = app._task_viewmodel.completedTasks
    driver.click(_row_control(driver, "Para transferi formu doğrulaması", CHECKBOX_OFFSET))
    driver.recorder.hold(1.4)
    expect(app._task_viewmodel.completedTasks == done + 1, "görev işaretlenmedi")


def kontrol_listesi(driver: Driver, app: Any) -> None:
    _open_featured_tasks(driver, app)
    badge = driver.find("2/4")
    driver.click(badge)
    driver.recorder.hold(0.4)
    driver.focus(_content(driver, CHECKLIST_TASK), driver.find("Hata mesajları"))
    driver.recorder.hold(0.5)
    driver.click(driver.find("Boş durum ekranı"))
    driver.recorder.hold(0.8)
    expect(bool(driver.matches("3/4")), "kontrol listesi maddesi işaretlenmedi")
    driver.click(driver.find("3/4"))  # Panel açıkken sürüklenecek satır listenin dışında kalıyor.
    driver.unfocus()
    driver.recorder.hold(0.5)
    driver.say()
    source = driver.center(_content(driver, "Biyometrik giriş"))
    # Satırın üst şeridine bırakmak "önüne taşı" demektir.
    target = driver.center(_content(driver, CHECKLIST_TASK)) + QPointF(0, -18)
    driver.drag(source, target)
    moved = scene_rect(_content(driver, "Biyometrik giriş")).y()
    expect(moved < scene_rect(_content(driver, CHECKLIST_TASK)).y(), "sürükle-bırak çalışmadı")
    driver.recorder.hold(1.0)


def arama(driver: Driver, app: Any) -> None:
    _menu(driver, "Fikirler")
    driver.recorder.hold(0.5)
    driver.say()
    driver.shortcut(Qt.Key.Key_K, Qt.KeyboardModifier.ControlModifier, "Ctrl + K")
    if not app._nav_bridge.searchModalOpen:
        # Qt kısayolu yalnızca etkin pencerede çalışır; çekim sırasında başka pencereye geçilmiş olabilir.
        logger.warning("Ctrl+K tetiklenmedi (pencere etkin değil); arama doğrudan açılıyor")
        app._nav_bridge.openSearch()
        driver.recorder.hold(0.6)
    expect(app._nav_bridge.searchModalOpen, "arama açılmadı")
    driver.recorder.hold(0.4)
    driver.type_text("transfer", frames_per_char=3)
    driver.recorder.hold(1.2)
    driver.click(driver.find("Para transferi formu doğrulaması"))
    driver.recorder.hold(1.4)
    expect(not app._nav_bridge.searchModalOpen, "arama sonucu açılmadı")


def notlar(driver: Driver, app: Any) -> None:
    _menu(driver, "Notlarım")
    driver.click(_content(driver, MEMO_TITLE))
    driver.recorder.hold(0.3)
    driver.click(driver.find("Çizim"))
    driver.recorder.hold(0.4)
    canvas = max(
        (i for i in driver.items() if i.metaObject().className().startswith("QQuickCanvasItem")),
        key=lambda i: i.width() * i.height(),
    )
    area = scene_rect(canvas)

    def at(x: float, y: float) -> QPointF:
        return QPointF(area.left() + area.width() * x, area.top() + area.height() * y)

    driver.click(driver.find("Oval"))
    driver.drag(at(0.08, 0.22), at(0.34, 0.50), 0.5)
    driver.drag(at(0.62, 0.22), at(0.88, 0.50), 0.5)
    driver.click(driver.find("Ok"))
    driver.drag(at(0.36, 0.36), at(0.60, 0.36), 0.5)
    driver.recorder.hold(1.0)


def analitik(driver: Driver, app: Any) -> None:
    _menu(driver, "Analitik")
    driver.recorder.settle()
    driver.recorder.hold(1.5)
    driver.focus(driver.find("Zaman İçinde Tamamlanan Görevler"), driver.find("En İyi Dönem"))
    driver.recorder.hold(2.0)
    driver.unfocus()
    driver.recorder.hold(0.5)
    driver.say()
    driver.scroll_to_bottom(2.4)
    driver.recorder.hold(1.2)


def tema(driver: Driver, app: Any) -> None:
    driver.recorder.hold(0.6)
    label = scene_rect(driver.find("Koyu Tema"))
    # Anahtarın metni yoktur; etiketin hemen sağındadır.
    driver.click(QPointF(label.right() + 30, label.center().y()))
    driver.recorder.hold(1.0)
    expect(not app._theme_bridge.isDark, "açık temaya geçilmedi")
    _menu(driver, "Ayarlar")
    for package in ("Emerald", "Violet"):
        driver.click(driver.find(package))
        driver.recorder.hold(0.4)
    driver.click(driver.find("Koyu"))
    driver.click(driver.find("Rose"))
    driver.recorder.hold(0.4)
    driver.say()
    _menu(driver, "Ana Panel")
    driver.recorder.hold(1.0)


SCENES: dict[str, Scene] = {
    "ana_panel": ana_panel,
    "fikir_proje": fikir_proje,
    "asamalar": asamalar,
    "gorev_agaci": gorev_agaci,
    "kontrol_listesi": kontrol_listesi,
    "arama": arama,
    "notlar": notlar,
    "analitik": analitik,
    "tema": tema,
}
