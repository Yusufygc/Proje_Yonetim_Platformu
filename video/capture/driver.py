"""Arayüzü görünen metinden bulup sentetik fare ve klavye ile sürer."""
from __future__ import annotations

from collections.abc import Callable, Iterator

from PySide6.QtCore import QEvent, QPoint, QPointF, QRectF, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtQuick import QQuickItem
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from recorder import FPS, TEMPO, WINDOW_SIZE, Recorder

LEFT = Qt.MouseButton.LeftButton
NO_MOD = Qt.KeyboardModifier.NoModifier


def walk(item: QQuickItem) -> Iterator[QQuickItem]:
    """Yalnızca görünür alt ağacı dolaşır."""
    if not item.isVisible() or item.opacity() == 0:
        return
    yield item
    for child in item.childItems():
        yield from walk(child)


def scene_rect(item: QQuickItem) -> QRectF:
    return item.mapRectToScene(QRectF(0, 0, item.width(), item.height()))


def clipped_away(item: QQuickItem, point: QPointF) -> bool:
    """Öğe, kırpan bir atasının (ör. kaydırılan liste) dışında kalıyorsa ekranda görünmez."""
    parent = item.parentItem()
    while parent is not None:
        if parent.clip() and not scene_rect(parent).contains(point):
            return True
        parent = parent.parentItem()
    return False


def ease(t: float) -> float:
    return 4 * t**3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


class Driver:
    def __init__(self, recorder: Recorder) -> None:
        self.recorder = recorder
        self.window = recorder.window

    def items(self) -> list[QQuickItem]:
        return list(walk(self.window.contentItem()))

    def scroll_to_bottom(self, seconds: float) -> None:
        """En büyük kaydırılabilir alanı yumuşakça sona getirir; tekerlek olayı gibi sıçramaz."""
        areas = [
            i for i in self.items()
            if i.property("contentY") is not None and (i.property("contentHeight") or 0) > i.height() + 40
        ]
        expect(bool(areas), "kaydırılabilir alan yok")
        area = max(areas, key=lambda i: i.width() * i.height())
        start = float(area.property("contentY"))
        end = float(area.property("contentHeight")) - area.height()
        steps = round(seconds * TEMPO * FPS)
        for index in range(1, steps + 1):
            area.setProperty("contentY", start + (end - start) * ease(index / steps))
            self.recorder.frame()

    def matches(
        self, text: str, where: Callable[[QRectF], bool] | None = None
    ) -> list[QQuickItem]:
        """`text` veya `placeholderText` değeri tam eşleşen görünür öğeler, yukarıdan aşağıya."""
        screen = QRectF(0, 0, *WINDOW_SIZE)
        found = []
        for item in walk(self.window.contentItem()):
            if text not in (item.property("text"), item.property("placeholderText")):
                continue
            rect = scene_rect(item)
            if rect.width() <= 0 or not screen.contains(rect.center()) or clipped_away(item, rect.center()):
                continue
            if where is None or where(rect):
                found.append(item)
        # Düğme ile içindeki yazı aynı metni taşır; dıştaki öğe tek eşleşme sayılır.
        outer = [i for i in found if not any(o is not i and scene_rect(o).contains(scene_rect(i)) for o in found)]
        return sorted(outer, key=lambda i: (scene_rect(i).y(), scene_rect(i).x()))

    def find(self, text: str, where: Callable[[QRectF], bool] | None = None) -> QQuickItem:
        """Tek eşleşme ister; belirsizlikte sessizce yanlış yere tıklamak yerine hata verir."""
        found = self.matches(text, where)
        if len(found) != 1:
            places = [scene_rect(i).toRect().getRect() for i in found]
            raise LookupError(f"'{text}' için {len(found)} eşleşme: {places}")
        return found[0]

    def center(self, item: QQuickItem) -> QPointF:
        return scene_rect(item).center()

    def move(self, target: QPointF, seconds: float = 0.6) -> None:
        """İmleci yumuşak hızlanma ve yavaşlamayla taşır; fare üstü efektleri de tetiklenir."""
        start_x, start_y = self.recorder.cursor
        steps = max(1, round(seconds * TEMPO * FPS))
        for index in range(1, steps + 1):
            progress = ease(index / steps)
            x = start_x + (target.x() - start_x) * progress
            y = start_y + (target.y() - start_y) * progress
            self.recorder.cursor = (x, y)
            QTest.mouseMove(self.window, QPoint(round(x), round(y)))
            self.recorder.frame()

    def click(self, target: QQuickItem | QPointF, pause: float = 0.25) -> None:
        point = target if isinstance(target, QPointF) else self.center(target)
        self.move(point)
        self.recorder.hold(pause)  # İzleyici hedefi görsün.
        self.recorder.mark_click()
        QTest.mousePress(self.window, LEFT, NO_MOD, point.toPoint())
        self.recorder.hold(0.1)
        QTest.mouseRelease(self.window, LEFT, NO_MOD, point.toPoint())
        self.recorder.hold(0.35)

    def drag(self, source: QPointF, target: QPointF, seconds: float = 1.2) -> None:
        self.move(source)
        self.recorder.hold(0.2)
        self.recorder.mark_click()
        QTest.mousePress(self.window, LEFT, NO_MOD, source.toPoint())
        self.recorder.hold(0.2)
        self.move(target, seconds)
        self.recorder.hold(0.3)
        QTest.mouseRelease(self.window, LEFT, NO_MOD, target.toPoint())
        self.recorder.hold(0.6)

    def _text_target(self) -> QQuickItem:
        """Klavyenin gideceği metin alanı. Pencere etkin değilken etkin odak boş kalabildiği için
        yedek olarak odağı istenmiş tek görünür metin alanı kullanılır."""
        active = self.window.activeFocusItem()
        if active is not None and active.property("cursorPosition") is not None:
            return active
        focused = [
            i for i in self.items()
            if i.property("cursorPosition") is not None and i.property("focus")
        ]
        expect(len(focused) == 1, f"yazılacak alan belirsiz: {len(focused)} aday")
        return focused[0]

    def type_text(self, text: str, frames_per_char: int = 2) -> None:
        """Türkçe karakterler tuş koduyla gönderilemediğinden metin taşıyan tuş olayı kullanılır.

        Olaylar pencereye değil odaktaki alana gider: çekim sırasında başka bir yere tıklanıp
        pencere etkinliğini yitirirse harfler sessizce kayboluyordu.
        """
        field = self._text_target()
        for char in text:
            for kind in (QEvent.Type.KeyPress, QEvent.Type.KeyRelease):
                QApplication.sendEvent(field, QKeyEvent(kind, 0, NO_MOD, char))
            for _ in range(frames_per_char):
                self.recorder.frame()
        written = str(field.property("text"))
        expect(written == text, f"metin eksik yazıldı: '{written}', beklenen '{text}'")

    def say(self) -> None:
        """Senaryodaki sıradaki cümle bu andan önce okunmasın."""
        self.recorder.mark("say")

    def toast(self) -> QQuickItem:
        pending = [self.window.contentItem()]
        while pending:
            item = pending.pop()
            if item.metaObject().className().startswith("ToastNotification"):
                return item
            pending.extend(item.childItems())
        raise LookupError("ToastNotification bulunamadı")

    def dismiss_toast(self) -> None:
        """Çekimde bildirim kendiliğinden kapanmaz; arkasındaki içeriği örtmeden kapatılır."""
        self.toast().setProperty("opacity", 0.0)
        self.recorder.hold(0.4)

    def shortcut(self, key: Qt.Key, modifier: Qt.KeyboardModifier, label: str) -> None:
        self.recorder.mark("shortcut", label=label)
        QTest.keyClick(self.window, key, modifier)
        self.recorder.hold(0.6)

    def focus(self, *items: QQuickItem) -> None:
        """Kamera bu öğelerin birleşik alanına yaklaşsın."""
        rect = scene_rect(items[0])
        for item in items[1:]:
            rect = rect.united(scene_rect(item))
        self.recorder.mark("focus", rect=[rect.x(), rect.y(), rect.width(), rect.height()])

    def unfocus(self) -> None:
        self.recorder.mark("focus", rect=None)
