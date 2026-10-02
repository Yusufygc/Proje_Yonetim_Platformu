import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"

Item {
    id: archiveViewRoot
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
                    name: "archive"
                    size: 48
                    color: themeBridge.textMuted
                    anchors.horizontalCenter: parent.horizontalCenter
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: i18nBridge.tr("archive_title", "Arşiv")
                    font.pixelSize: 16
                    font.weight: Font.DemiBold
                    color: themeBridge.textPrimary
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: i18nBridge.tr("archive_desc", "Adım 5 kapsamında arşivlenen projeleri listeleme ve geri yükleme eklenecektir.")
                    font.pixelSize: 13
                    color: themeBridge.textSecondary
                }
            }
        }
    }
}
