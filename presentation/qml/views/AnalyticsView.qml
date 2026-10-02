import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"

Item {
    id: analyticsViewRoot
    anchors.fill: parent

    Column {
        anchors.fill: parent
        padding: 24
        spacing: 16

        AppCard {
            width: parent.width - 48
            height: parent.height - 48

            Column {
                anchors.centerIn: parent
                spacing: 12

                AppIcon {
                    name: "chart-bar"
                    size: 48
                    color: themeBridge.accentStart
                    anchors.horizontalCenter: parent.horizontalCenter
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: i18nBridge.tr("analytics_title", "Analitik & Metrikler")
                    font.pixelSize: 16
                    font.weight: Font.DemiBold
                    color: themeBridge.textPrimary
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: i18nBridge.tr("analytics_desc", "Adım 5 kapsamında proje performansı ve tamamlanma grafikleri eklenecektir.")
                    font.pixelSize: 13
                    color: themeBridge.textSecondary
                }
            }
        }
    }
}
