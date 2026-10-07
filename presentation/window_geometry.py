"""Ana pencerenin ekrana yerleşimi: kayıtlı konumu geri yükleme, sığdırma ve kaydetme.

Qt'de `QWindow.geometry()` yalnızca **istemci alanını** (başlık çubuğu hariç) verir. Konumu ekranın
kullanılabilir alanının en üstüne (`avail.top()`) koymak başlık çubuğunu ekranın dışına iter;
küçült/büyüt/kapat düğmeleri görünmez olur. Bu yüzden her yerleşimde çerçeve payı hesaba katılır.
"""
from __future__ import annotations

from PySide6.QtCore import QRect, QTimer
from PySide6.QtGui import QCursor, QScreen, QWindow
from PySide6.QtQuick import QQuickWindow
from PySide6.QtWidgets import QApplication

from core.managers.preference_manager import PreferenceManager

# Çerçeve payı henüz bilinmiyorsa (pencere gösterilmeden önce) kullanılan güvenli başlık çubuğu yüksekliği.
_FALLBACK_TITLE_BAR_PX = 40
_DEFAULT_MAX_SIZE = (1280, 800)
_MIN_SIZE = (800, 520)


def frame_top_margin(win: QWindow) -> int:
    """Başlık çubuğunun istemci alanının üstünde kapladığı yükseklik."""
    margin = win.frameMargins().top()
    return margin if margin > 0 else _FALLBACK_TITLE_BAR_PX


def fit_rect_to_screen(saved: QRect, avail: QRect, top_margin: int) -> QRect:
    """Kayıtlı istemci dikdörtgenini, başlık çubuğu dahil ekranın kullanılabilir alanına sığdırır."""
    width = min(saved.width(), avail.width())
    height = min(saved.height(), avail.height() - top_margin)
    min_x, max_x = avail.left(), avail.left() + avail.width() - width
    min_y = avail.top() + top_margin
    max_y = max(min_y, avail.top() + avail.height() - height)
    x = max(min_x, min(saved.x(), max_x))
    y = max(min_y, min(saved.y(), max_y))
    return QRect(x, y, width, height)


def centered_rect(screen: QScreen) -> QRect:
    """Ekranın kullanılabilir alanında ortalanmış varsayılan pencere dikdörtgeni."""
    avail = screen.availableGeometry()
    max_w, max_h = _DEFAULT_MAX_SIZE
    min_w, min_h = _MIN_SIZE
    width = min(avail.width(), min(max_w, max(min_w, int(avail.width() * 0.92))))
    height = min(avail.height(), min(max_h, max(min_h, int(avail.height() * 0.88))))
    x = avail.x() + max(0, (avail.width() - width) // 2)
    y = avail.y() + max(0, (avail.height() - height) // 2)
    return QRect(x, y, width, height)


def _covers_screen(rect: QRect, avail: QRect) -> bool:
    """Dikdörtgen kullanılabilir alanı tamamen kaplıyorsa büyütülmüş pencere sayılır."""
    return rect.width() >= avail.width() and rect.height() >= avail.height() - _FALLBACK_TITLE_BAR_PX


def _keep_frame_on_screen(win: QWindow) -> None:
    """Pencere gösterildikten sonra gerçek çerçeveyi ölçüp ekranın dışına taşan kısmı düzeltir."""
    screen = win.screen()
    if screen is None or win.visibility() != QWindow.Visibility.Windowed:
        return
    avail = screen.availableGeometry()
    frame = win.frameGeometry()
    if frame.top() < avail.top():
        win.setY(win.y() + avail.top() - frame.top())
    overflow = win.frameGeometry().bottom() - avail.bottom()
    if overflow > 0:
        win.setHeight(max(_MIN_SIZE[1], win.height() - overflow))


def _bind_geometry_persistence(win: QQuickWindow, prefs: PreferenceManager) -> None:
    """Kapanışta pencerenin NORMAL (büyütülmemiş) konumunu ve büyütülmüş olup olmadığını kaydeder.

    Büyütülmüş pencerenin geometrisi kaydedilirse, kullanıcı küçülttüğünde pencere tam ekran boyutunda
    ve başlık çubuğu ekranın dışında açılır; bu yüzden yalnızca Windowed durumdaki geometri izlenir.
    """
    normal = {"rect": win.geometry()}

    def remember() -> None:
        screen = win.screen()
        if win.visibility() != QWindow.Visibility.Windowed or screen is None:
            return
        if not _covers_screen(win.geometry(), screen.availableGeometry()):
            normal["rect"] = win.geometry()

    def save() -> None:
        rect = normal["rect"]
        is_max = win.visibility() == QWindow.Visibility.Maximized
        prefs.save_window_rect(rect.x(), rect.y(), rect.width(), rect.height(), is_max)

    for signal in (win.xChanged, win.yChanged, win.widthChanged, win.heightChanged):
        signal.connect(remember)
    win.closing.connect(save)


def setup_window_geometry(win: QQuickWindow, prefs: PreferenceManager, app: QApplication) -> None:
    """Pencereyi kayıtlı konuma veya aktif ekranda sınırları aşmayacak şekilde yerleştirir."""
    saved = prefs.load_window_rect()
    restored = False
    if saved:
        sx, sy, sw, sh, is_max = saved
        probe = QRect(sx, sy, min(sw, 200), min(sh, 40))
        target_screen = next((s for s in app.screens() if s.availableGeometry().intersects(probe)), None)
        if target_screen:
            win.setGeometry(fit_rect_to_screen(QRect(sx, sy, sw, sh), target_screen.availableGeometry(), frame_top_margin(win)))
            if is_max:
                win.showMaximized()
            restored = True

    if not restored:
        screens = app.screens()
        target = app.screenAt(QCursor.pos()) or app.primaryScreen() or (screens[0] if screens else None)
        if target:
            win.setGeometry(centered_rect(target))

    _bind_geometry_persistence(win, prefs)
    QTimer.singleShot(0, lambda: _keep_frame_on_screen(win))
