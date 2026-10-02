import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"

Item {
    id: memoViewRoot
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
                    name: "note-sticky"
                    size: 48
                    color: themeBridge.warning
                    anchors.horizontalCenter: parent.horizontalCenter
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: i18nBridge.tr("memo_title", "Notlarım (Memos)")
                    font.pixelSize: 16
                    font.weight: Font.DemiBold
                    color: themeBridge.textPrimary
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: i18nBridge.tr("memo_desc", "Adım 4 kapsamında renkli yapışkan notlar grid görünümü eklenecektir.")
                    font.pixelSize: 13
                    color: themeBridge.textSecondary
                }
            }
        }
    }
}
