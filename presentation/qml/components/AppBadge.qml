import QtQuick 2.15

Rectangle {
    id: badgeRoot

    property string text: ""
    property string variant: "accent" // "accent" | "neutral" | "success" | "warning" | "danger"
    property string size: "md" // "sm" | "md" | "lg"
    // Durum bildiren rozetlerde (öncelik, sağlık) yazının önünde renkli nokta gösterilir.
    property bool showDot: false

    readonly property color resolvedColor: {
        switch (variant) {
            case "neutral": return themeBridge.textSecondary;
            case "success": return themeBridge.success;
            case "warning": return themeBridge.warning;
            case "danger": return themeBridge.danger;
            case "accent":
            default: return themeBridge.accentStart;
        }
    }

    property color badgeColor: resolvedColor
    // Yazı, zemin tonuyla aynı hue'da kalır ama temaya göre koyulaşır/açılır; açık zeminde turuncu/sarı yazı okunmuyordu.
    property color textColor: themeBridge.isDark ? Qt.lighter(badgeColor, 1.3) : Qt.darker(badgeColor, 1.55)

    implicitWidth: badgeRow.implicitWidth + (size === "sm" ? 12 : 18)
    implicitHeight: size === "sm" ? 18 : (size === "lg" ? 26 : 22)
    radius: 999
    color: Qt.rgba(badgeColor.r, badgeColor.g, badgeColor.b, themeBridge.isDark ? 0.18 : 0.14)
    border.width: 1
    border.color: Qt.rgba(badgeColor.r, badgeColor.g, badgeColor.b, themeBridge.isDark ? 0.4 : 0.3)

    Row {
        id: badgeRow
        anchors.centerIn: parent
        spacing: 5

        Rectangle {
            visible: badgeRoot.showDot
            width: 6
            height: 6
            radius: 3
            color: badgeRoot.badgeColor
            anchors.verticalCenter: parent.verticalCenter
        }

        Text {
            id: badgeText
            text: badgeRoot.text
            font.pixelSize: badgeRoot.size === "sm" ? 10 : (badgeRoot.size === "lg" ? 12 : 11)
            font.weight: Font.DemiBold
            color: badgeRoot.textColor
            anchors.verticalCenter: parent.verticalCenter
        }
    }
}
