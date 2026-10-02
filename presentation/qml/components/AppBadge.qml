import QtQuick 2.15

Rectangle {
    id: badgeRoot

    property string text: ""
    property string variant: "accent" // "accent" | "neutral" | "success" | "warning" | "danger"

    readonly property color resolvedColor: {
        switch (variant) {
            case "neutral": return themeBridge.textSecondary;
            case "success": return "#10B981";
            case "warning": return "#F59E0B";
            case "danger": return "#EF4444";
            case "accent":
            default: return themeBridge.accentStart;
        }
    }

    property color badgeColor: resolvedColor
    property color textColor: resolvedColor

    implicitWidth: badgeText.implicitWidth + 16
    implicitHeight: 22
    radius: 999
    color: Qt.rgba(badgeColor.r, badgeColor.g, badgeColor.b, 0.15)
    border.width: 1
    border.color: Qt.rgba(badgeColor.r, badgeColor.g, badgeColor.b, 0.35)

    Text {
        id: badgeText
        anchors.centerIn: parent
        text: badgeRoot.text
        font.pixelSize: 11
        font.weight: Font.DemiBold
        color: badgeRoot.textColor
    }
}
