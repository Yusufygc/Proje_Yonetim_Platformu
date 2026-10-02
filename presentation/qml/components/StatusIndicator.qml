import QtQuick 2.15

Row {
    id: root

    property string status: "PLANNED" // PLANNED, ACTIVE, ON_HOLD, BLOCKED, COMPLETED, CANCELLED
    property bool showLabel: true
    property int dotSize: 8

    spacing: 6

    readonly property color statusColor: {
        switch (root.status) {
            case "ACTIVE": return themeBridge.success;
            case "COMPLETED": return themeBridge.success;
            case "ON_HOLD": return themeBridge.warning;
            case "BLOCKED": return themeBridge.danger;
            case "CANCELLED": return themeBridge.danger;
            default: return themeBridge.textSecondary;
        }
    }

    readonly property string statusText: {
        switch (root.status) {
            case "PLANNED": return i18nBridge.tr("status_planned", "Planlandı");
            case "ACTIVE": return i18nBridge.tr("status_active", "Aktif");
            case "ON_HOLD": return i18nBridge.tr("status_on_hold", "Beklemede");
            case "BLOCKED": return i18nBridge.tr("status_blocked", "Engellendi");
            case "COMPLETED": return i18nBridge.tr("status_completed", "Tamamlandı");
            case "CANCELLED": return i18nBridge.tr("status_cancelled", "İptal Edildi");
            default: return root.status;
        }
    }

    Rectangle {
        width: root.dotSize
        height: root.dotSize
        radius: root.dotSize / 2
        color: root.statusColor
        anchors.verticalCenter: parent.verticalCenter
    }

    Text {
        visible: root.showLabel
        text: root.statusText
        font.pixelSize: 11
        font.weight: Font.Medium
        color: root.statusColor
        anchors.verticalCenter: parent.verticalCenter
    }
}
