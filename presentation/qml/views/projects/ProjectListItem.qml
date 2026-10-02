import QtQuick 2.15
import QtQuick.Controls 2.15
import "../../components"

Rectangle {
    id: root

    property int projectId: 0
    property string title: ""
    property string projectType: ""
    property string status: "PLANNED"
    property string priority: "MEDIUM"
    property int progress: 0
    property bool isSelected: false

    signal clicked()

    width: parent ? parent.width : 260
    height: 72
    radius: 10

    color: {
        if (root.isSelected) return themeBridge.isDark ? Qt.rgba(0.38, 0.42, 0.95, 0.22) : "#EEF2FF";
        if (mouseArea.containsMouse) return themeBridge.surfaceRaised;
        return themeBridge.surface;
    }

    border.width: root.isSelected ? 2 : 1
    border.color: root.isSelected ? themeBridge.accentStart : themeBridge.border

    Behavior on color { ColorAnimation { duration: 120 } }
    Behavior on border.color { ColorAnimation { duration: 120 } }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: root.clicked()
    }

    Column {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 6

        // Üst Satır: Başlık ve Öncelik Rozeti
        Row {
            width: parent.width
            spacing: 8

            Text {
                width: parent.width - (priorityBadge.visible ? priorityBadge.width + 8 : 0)
                text: root.title
                font.pixelSize: 13
                font.weight: Font.DemiBold
                color: root.isSelected ? themeBridge.accentStart : themeBridge.textPrimary
                elide: Text.ElideRight
                anchors.verticalCenter: parent.verticalCenter
            }

            AppBadge {
                id: priorityBadge
                visible: root.priority !== ""
                text: {
                    switch (root.priority) {
                        case "CRITICAL": return i18nBridge.tr("priority_critical", "Kritik");
                        case "HIGH": return i18nBridge.tr("priority_high", "Yüksek");
                        case "LOW": return i18nBridge.tr("priority_low", "Düşük");
                        default: return i18nBridge.tr("priority_medium", "Orta");
                    }
                }
                badgeColor: {
                    switch (root.priority) {
                        case "CRITICAL": return themeBridge.danger;
                        case "HIGH": return themeBridge.warning;
                        case "LOW": return themeBridge.textSecondary;
                        default: return themeBridge.accentStart;
                    }
                }
                anchors.verticalCenter: parent.verticalCenter
            }
        }

        // Alt Satır: Durum Göstergesi ve İlerleme Çubuğu
        Item {
            width: parent.width
            height: 20

            StatusIndicator {
                status: root.status
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter
            }

            AppProgressBar {
                value: root.progress
                showLabel: true
                barHeight: 4
                implicitWidth: 80
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
            }
        }
    }
}
