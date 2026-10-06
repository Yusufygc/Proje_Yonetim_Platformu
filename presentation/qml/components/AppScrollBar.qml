import QtQuick 2.15
import QtQuick.Controls 2.15

ScrollBar {
    id: control

    policy: ScrollBar.AsNeeded
    hoverEnabled: true
    interactive: true

    implicitWidth: orientation === Qt.Vertical ? 8 : 24
    implicitHeight: orientation === Qt.Horizontal ? 8 : 24

    visible: policy === ScrollBar.AlwaysOn || (size < 1.0 && size > 0.0)
    opacity: (policy === ScrollBar.AlwaysOn || active || hovered || pressed) ? 1.0 : 0.0
    Behavior on opacity { NumberAnimation { duration: 150 } }

    contentItem: Rectangle {
        implicitWidth: control.orientation === Qt.Vertical ? (control.hovered || control.pressed ? 8 : 6) : 24
        implicitHeight: control.orientation === Qt.Horizontal ? (control.hovered || control.pressed ? 8 : 6) : 24
        radius: 4
        visible: control.policy === ScrollBar.AlwaysOn || control.size < 1.0
        color: {
            if (control.pressed || control.hovered) return themeBridge.accentStart;
            return themeBridge.isDark ? Qt.rgba(1, 1, 1, 0.45) : Qt.rgba(0, 0, 0, 0.35);
        }

        Behavior on color { ColorAnimation { duration: 120 } }
        Behavior on implicitWidth { NumberAnimation { duration: 100 } }
        Behavior on implicitHeight { NumberAnimation { duration: 100 } }
    }

    background: Rectangle {
        implicitWidth: control.orientation === Qt.Vertical ? 8 : 24
        implicitHeight: control.orientation === Qt.Horizontal ? 8 : 24
        radius: 4
        visible: control.policy === ScrollBar.AlwaysOn || control.size < 1.0
        color: (control.hovered || control.pressed) ?
            (themeBridge.isDark ? Qt.rgba(1, 1, 1, 0.08) : Qt.rgba(0, 0, 0, 0.06)) :
            "transparent"
    }
}
