import QtQuick 2.15
import QtQuick.Controls 2.15

AbstractButton {
    id: control

    property string variant: "secondary" // "primary", "secondary", "ghost", "danger"
    property alias btnVariant: control.variant
    property string iconName: ""
    property int iconSize: 16
    property int radius: 8

    implicitWidth: {
        if (control.text === "" && control.iconName !== "") return control.iconSize + 16;
        if (control.text.length <= 2 && control.iconName === "") return 36;
        return contentLayout.implicitWidth + 24;
    }
    implicitHeight: 36

    hoverEnabled: true

    MouseArea {
        anchors.fill: parent
        cursorShape: Qt.PointingHandCursor
        acceptedButtons: Qt.NoButton
    }

    background: Rectangle {
        id: bgRect
        radius: control.radius
        border.width: control.variant === "ghost" ? 0 : 1
        border.color: {
            if (control.variant === "primary") return "transparent";
            if (control.variant === "danger") return themeBridge.danger;
            if (control.variant === "warning") return themeBridge.warning;
            return control.hovered ? themeBridge.accentStart : themeBridge.border;
        }

        color: {
            if (!control.enabled) return themeBridge.isDark ? themeBridge.surfaceAlt : themeBridge.border;
            if (control.variant === "primary") {
                return control.pressed ? themeBridge.accentEnd : (control.hovered ? themeBridge.accentEnd : themeBridge.accentStart);
            }
            if (control.variant === "danger") {
                var dc = Qt.color(themeBridge.danger);
                return control.hovered ? Qt.rgba(dc.r, dc.g, dc.b, themeBridge.isDark ? 0.25 : 0.12) : "transparent";
            }
            if (control.variant === "warning") {
                var wc = Qt.color(themeBridge.warning);
                return control.hovered ? Qt.rgba(wc.r, wc.g, wc.b, themeBridge.isDark ? 0.25 : 0.12) : "transparent";
            }
            if (control.variant === "ghost") {
                return control.hovered ? themeBridge.hoverOverlay : "transparent";
            }
            // secondary
            return control.hovered ? themeBridge.surfaceRaised : themeBridge.surface;
        }

        Behavior on color { ColorAnimation { duration: 150 } }
        Behavior on border.color { ColorAnimation { duration: 150 } }
    }

    contentItem: Item {
        Row {
            id: contentLayout
            anchors.centerIn: parent
            spacing: (control.iconName !== "" && control.text !== "") ? 8 : 0

            AppIcon {
                id: btnIcon
                visible: control.iconName !== ""
                name: control.iconName
                size: control.iconSize
                color: {
                    if (control.variant === "primary") return themeBridge.iconOnAccent;
                    if (control.variant === "danger") return themeBridge.danger;
                    if (control.variant === "warning") return themeBridge.warning;
                    return control.hovered ? themeBridge.accentStart : themeBridge.textPrimary;
                }
                anchors.verticalCenter: parent.verticalCenter
            }

            Text {
                id: btnText
                visible: control.text !== ""
                text: control.text
                font.pixelSize: control.text.length <= 2 ? 15 : 13
                font.weight: control.variant === "primary" ? Font.Medium : Font.Normal
                color: {
                    if (!control.enabled) return themeBridge.textMuted;
                    if (control.variant === "primary") return themeBridge.iconOnAccent;
                    if (control.variant === "danger") return themeBridge.danger;
                    if (control.variant === "warning") return themeBridge.warning;
                    return control.hovered ? themeBridge.accentStart : themeBridge.textPrimary;
                }
                anchors.verticalCenter: parent.verticalCenter
                Behavior on color { ColorAnimation { duration: 150 } }
            }
        }
    }

    scale: control.pressed ? 0.98 : 1.0
    Behavior on scale { NumberAnimation { duration: 100; easing.type: Easing.OutQuad } }
}
