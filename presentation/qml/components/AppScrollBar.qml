import QtQuick 2.15
import QtQuick.Controls 2.15

ScrollBar {
    id: control

    policy: ScrollBar.AsNeeded
    hoverEnabled: true
    interactive: true

    implicitWidth: 8
    implicitHeight: 8

    contentItem: Rectangle {
        implicitWidth: control.hovered || control.pressed ? 8 : 6
        implicitHeight: control.hovered || control.pressed ? 8 : 6
        radius: 4
        color: {
            if (control.pressed || control.hovered) return themeBridge.accentStart;
            return themeBridge.isDark ? Qt.rgba(1, 1, 1, 0.45) : Qt.rgba(0, 0, 0, 0.35);
        }
        opacity: (control.policy === ScrollBar.AlwaysOn || control.active || control.hovered || control.pressed) ? 1.0 : 0.85

        Behavior on color { ColorAnimation { duration: 120 } }
        Behavior on opacity { NumberAnimation { duration: 150 } }
        Behavior on implicitWidth { NumberAnimation { duration: 100 } }
    }

    background: Rectangle {
        implicitWidth: 8
        radius: 4
        color: (control.hovered || control.pressed) ?
            (themeBridge.isDark ? Qt.rgba(1, 1, 1, 0.08) : Qt.rgba(0, 0, 0, 0.06)) :
            "transparent"
    }
}
