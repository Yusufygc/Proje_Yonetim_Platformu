import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../../components"
import "../../../theme"

// Proje detay sekme çubuğu (segmented tabs).
Rectangle {
    id: root

    property int currentTab: 0
    signal tabSelected(int index)

    height: 40
    radius: 8
    color: themeBridge.surfaceAlt
    border.width: 1
    border.color: themeBridge.border

    Row {
        anchors.centerIn: parent
        spacing: 4

        Repeater {
            model: [
                i18nBridge.tr("tab_summary", "Özet"),
                i18nBridge.tr("tab_tasks", "Görevler"),
                i18nBridge.tr("tab_decisions", "Kararlar"),
                i18nBridge.tr("tab_notes", "Notlar"),
                i18nBridge.tr("tab_resources", "Kaynaklar"),
                i18nBridge.tr("tab_outputs", "Çıktılar"),
                i18nBridge.tr("tab_activity", "Geçmiş")
            ]

            Rectangle {
                id: tabBtn
                width: Math.max(76, tabText.implicitWidth + 24)
                height: 32
                radius: 6
                color: root.currentTab === index ?
                    themeBridge.surfaceRaised :
                    (tabMouse.containsMouse ? (themeBridge.isDark ? themeBridge.surfaceRaised : themeBridge.border) : "transparent")
                border.width: root.currentTab === index ? 1 : 0
                border.color: themeBridge.border

                Text {
                    id: tabText
                    anchors.centerIn: parent
                    text: modelData
                    font.pixelSize: 12
                    font.weight: root.currentTab === index ? Font.DemiBold : Font.Normal
                    color: root.currentTab === index ? themeBridge.accentStart : themeBridge.textSecondary
                }

                MouseArea {
                    id: tabMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.tabSelected(index)
                }
            }
        }
    }
}
