import QtQuick 2.15

Row {
    id: root

    property string status: "PLANNED" // PLANNED, ACTIVE, ON_HOLD, BLOCKED, COMPLETED, CANCELLED
    property bool showLabel: true
    property int dotSize: 8

    spacing: 6

    readonly property color statusColor: {
        switch (root.status) {
            case "ACTIVE": case "IN_PROGRESS": case "DEVELOPING": return themeBridge.success;
            case "COMPLETED": case "DONE": case "APPROVED": return themeBridge.success;
            case "ON_HOLD": case "WAITING": case "REVIEW": case "REVIEWING": case "VALIDATING": return themeBridge.warning;
            case "BLOCKED": case "CANCELLED": case "REJECTED": return themeBridge.danger;
            case "TODO": case "NOT_STARTED": case "RAW": return themeBridge.accentStart;
            case "CONVERTED": case "ARCHIVED": case "DEFERRED": case "SKIPPED": return themeBridge.textMuted;
            default: return themeBridge.textSecondary;
        }
    }

    readonly property string statusText: {
        switch (root.status) {
            case "PLANNED": return i18nBridge.tr("status_planned", "Planlandı");
            case "ACTIVE": return i18nBridge.tr("status_active", "Aktif");
            case "ON_HOLD": return i18nBridge.tr("status_on_hold", "Beklemede");
            case "BLOCKED": return i18nBridge.tr("status_blocked", "Engellendi");
            case "COMPLETED": case "DONE": return i18nBridge.tr("status_completed", "Tamamlandı");
            case "CANCELLED": return i18nBridge.tr("status_cancelled", "İptal Edildi");
            case "ARCHIVED": return i18nBridge.tr("status_archived", "Arşivlendi");
            case "TODO": return i18nBridge.tr("status_todo", "Yapılacak");
            case "IN_PROGRESS": return i18nBridge.tr("status_in_progress", "Devam Ediyor");
            case "WAITING": return i18nBridge.tr("task_status_waiting", "Bekliyor");
            case "NOT_STARTED": return i18nBridge.tr("status_not_started", "Başlamadı");
            case "SKIPPED": return i18nBridge.tr("status_skipped", "Atlandı");
            case "RAW": return i18nBridge.tr("status_raw", "Ham Fikir");
            case "DEVELOPING": return i18nBridge.tr("status_developing", "Geliştiriliyor");
            case "REVIEW": case "REVIEWING": return i18nBridge.tr("idea_status_reviewing", "İnceleniyor");
            case "VALIDATING": return i18nBridge.tr("idea_status_validating", "Doğrulanıyor");
            case "APPROVED": return i18nBridge.tr("decision_approved", "Onaylandı");
            case "REJECTED": return i18nBridge.tr("decision_rejected", "Reddedildi");
            case "CONVERTED": return i18nBridge.tr("idea_status_converted", "Projeye Dönüştürüldü");
            case "DEFERRED": return i18nBridge.tr("idea_status_deferred", "Ertelendi");
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
