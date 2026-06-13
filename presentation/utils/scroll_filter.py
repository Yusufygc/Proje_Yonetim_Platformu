"""
Uygulama genelinde scroll davranışlarını düzenleyen Event Filter sınıfı.
"""
from PySide6.QtCore import QEvent, QObject
from PySide6.QtWidgets import QAbstractSpinBox, QApplication, QComboBox, QTabBar


class WheelEventFilter(QObject):
    """
    QComboBox, QSpinBox gibi giriş alanlarında ve QTabBar'da
    mouse wheel ile istenmeyen değişimleri engeller.
    """
    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.Wheel:
            if isinstance(obj, (QComboBox, QAbstractSpinBox, QTabBar)):
                # Bu widget'ların kendi wheel olayını işlemesini (değer değiştirmesini) engelle
                event.ignore()
                
                # Eğer scroll edilebilir bir formun içindeysek,
                # kaydırma işleminin devam etmesi için eventi üst (parent) widget'a gönder.
                parent = obj.parentWidget()
                if parent:
                    QApplication.sendEvent(parent, event)
                
                return True
        return super().eventFilter(obj, event)
