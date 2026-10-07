import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"
import "../theme"

// Yeni sürüm bulunduğunda çıkan güncelleme penceresi; indirirken kapatılamaz.
Rectangle {
    id: root

    visible: updateViewModel ? updateViewModel.isDialogOpen : false
    anchors.fill: parent
    color: "#80000000"
    z: 1000

    MouseArea {
        anchors.fill: parent
        onClicked: { /* modal diyalog dışı tıklamayı engeller */ }
    }

    Shortcut {
        sequence: "Escape"
        enabled: root.visible
        onActivated: updateViewModel.dismiss()
    }

    AppCard {
        width: Math.min(parent.width - 48, 460)
        height: content.implicitHeight + 2 * Theme.spacing.xl
        anchors.centerIn: parent

        ColumnLayout {
            id: content
            anchors.fill: parent
            anchors.margins: Theme.spacing.xl
            spacing: Theme.spacing.md

            RowLayout {
                Layout.fillWidth: true
                spacing: Theme.spacing.sm

                AppIcon {
                    name: "circle-info"
                    size: 22
                    color: Theme.accent(themeBridge.currentTheme)
                }

                Text {
                    text: i18nBridge.tr("update_dialog_title", "Yeni güncelleme var")
                    font.pixelSize: Theme.typography.sizeH3
                    font.weight: Theme.typography.weightBold
                    color: themeBridge.textPrimary
                    Layout.fillWidth: true
                }
            }

            Text {
                text: i18nBridge.tr("update_dialog_message", "Yeni bir sürüm yayınlandı. Şimdi güncellemek ister misiniz?")
                font.pixelSize: Theme.typography.sizeBody
                color: themeBridge.textSecondary
                wrapMode: Text.Wrap
                Layout.fillWidth: true
            }

            Text {
                text: i18nBridge.tr("update_dialog_current", "Mevcut sürüm") + ": v" + updateViewModel.currentVersion
                      + "   →   " + i18nBridge.tr("update_dialog_latest", "Yeni sürüm") + ": v" + updateViewModel.latestVersion
                font.pixelSize: 12
                font.weight: Font.DemiBold
                color: themeBridge.textPrimary
                wrapMode: Text.Wrap
                Layout.fillWidth: true
            }

            ScrollView {
                Layout.fillWidth: true
                Layout.preferredHeight: Math.min(notesText.implicitHeight, 160)
                visible: updateViewModel.releaseNotes !== "" && !updateViewModel.isDownloading
                contentWidth: availableWidth
                clip: true

                Text {
                    id: notesText
                    width: parent.width
                    text: updateViewModel.releaseNotes
                    font.pixelSize: 12
                    color: themeBridge.textMuted
                    wrapMode: Text.Wrap
                }
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: Theme.spacing.xs
                visible: updateViewModel.isDownloading

                Text {
                    text: i18nBridge.tr("update_downloading", "İndiriliyor... Kurulum sırasında uygulama kapanıp yeniden açılır.")
                    font.pixelSize: 12
                    color: themeBridge.textMuted
                    wrapMode: Text.Wrap
                    Layout.fillWidth: true
                }

                AppProgressBar {
                    Layout.fillWidth: true
                    value: updateViewModel.downloadProgress
                    showLabel: true
                }
            }

            Text {
                visible: updateViewModel.errorMessage !== ""
                text: updateViewModel.errorMessage
                font.pixelSize: 12
                color: themeBridge.danger
                wrapMode: Text.Wrap
                Layout.fillWidth: true
            }

            RowLayout {
                Layout.alignment: Qt.AlignRight
                spacing: Theme.spacing.sm

                AppButton {
                    text: i18nBridge.tr("update_action_later", "Sonra")
                    btnVariant: "secondary"
                    enabled: !updateViewModel.isDownloading
                    onClicked: updateViewModel.dismiss()
                }

                AppButton {
                    text: i18nBridge.tr("update_action_now", "Güncelle")
                    btnVariant: "primary"
                    enabled: !updateViewModel.isDownloading
                    onClicked: updateViewModel.startUpdate()
                }
            }
        }
    }
}
