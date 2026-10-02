import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"

Item {
    id: infoViewRoot
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
                    name: "circle-info"
                    size: 48
                    color: themeBridge.accentStart
                    anchors.horizontalCenter: parent.horizontalCenter
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: i18nBridge.tr("app_name", "Proje Yönetim ve Takip Platformu")
                    font.pixelSize: 18
                    font.bold: true
                    color: themeBridge.textPrimary
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: "Sürüm 0.1.0 — PySide6 & QML Modern Mimarisi"
                    font.pixelSize: 13
                    color: themeBridge.textSecondary
                }
            }
        }
    }
}
