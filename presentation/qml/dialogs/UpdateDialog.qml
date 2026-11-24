import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"
import "../theme"

// Güncelleme penceresi; denetim, indirme, kurulum ve SAC engeli bekleme akışını yönetir.
Rectangle {
    id: root

    readonly property string st: updateViewModel ? updateViewModel.state : "idle"
    readonly property bool isBusy: st === "checking" || st === "downloading" || st === "installing"

    visible: updateViewModel ? updateViewModel.isDialogOpen : false
    anchors.fill: parent
    color: "#80000000"
    z: 1000

    MouseArea {
        anchors.fill: parent
        onClicked: {
            if (!root.isBusy) {
                updateViewModel.dismiss()
            }
        }
    }

    Shortcut {
        sequence: "Escape"
        enabled: root.visible && !root.isBusy
        onActivated: updateViewModel.dismiss()
    }

    Shortcut {
        sequences: ["Return", "Enter"]
        enabled: root.visible && root.st === "available"
        onActivated: updateViewModel.startUpdate()
    }

    AppCard {
        width: Math.min(parent.width - 48, 500)
        height: content.implicitHeight + 2 * Theme.spacing.xl
        anchors.centerIn: parent

        MouseArea {
            anchors.fill: parent
        }

        ColumnLayout {
            id: content
            anchors.fill: parent
            anchors.margins: Theme.spacing.xl
            spacing: Theme.spacing.md

            RowLayout {
                Layout.fillWidth: true
                spacing: Theme.spacing.sm

                AppIcon {
                    name: root.st === "error" || root.st === "blocked" ? "triangle-alert" : "circle-info"
                    size: 22
                    color: root.st === "error" || root.st === "blocked"
                        ? themeBridge.warning
                        : Theme.accent(themeBridge.currentTheme)
                }

                Text {
                    text: root.st === "available"
                        ? i18nBridge.tr("update_dialog_title", "Yeni güncelleme var")
                        : i18nBridge.tr("update_dialog_status_title", "Güncelleme")
                    font.pixelSize: Theme.typography.sizeH3
                    font.weight: Theme.typography.weightBold
                    color: themeBridge.textPrimary
                    Layout.fillWidth: true
                }
            }

            Text {
                visible: text.length > 0
                text: root.st === "available"
                    ? i18nBridge.tr("update_dialog_message", "Yeni bir sürüm yayınlandı. Şimdi güncellemek ister misiniz?")
                    : (updateViewModel ? updateViewModel.statusMessage : "")
                font.pixelSize: Theme.typography.sizeBody
                color: root.st === "error" || root.st === "blocked" ? themeBridge.danger : themeBridge.textSecondary
                wrapMode: Text.Wrap
                Layout.fillWidth: true
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: Theme.spacing.sm
                visible: updateViewModel && updateViewModel.latestVersion !== ""

                Text {
                    text: i18nBridge.tr("update_dialog_current", "Mevcut sürüm") + ": v" + updateViewModel.currentVersion
                    font.pixelSize: 12
                    font.weight: Font.DemiBold
                    color: themeBridge.textMuted
                }

                AppIcon {
                    name: "arrow-right"
                    size: 13
                    color: themeBridge.textMuted
                }

                Text {
                    text: i18nBridge.tr("update_dialog_latest", "Yeni sürüm") + ": v" + updateViewModel.latestVersion
                    font.pixelSize: 12
                    font.weight: Font.DemiBold
                    color: themeBridge.textPrimary
                    Layout.fillWidth: true
                    elide: Text.ElideRight
                }
            }

            ScrollView {
                Layout.fillWidth: true
                Layout.preferredHeight: Math.min(notesText.implicitHeight, 160)
                visible: root.st === "available" && updateViewModel.releaseNotes !== ""
                contentWidth: availableWidth
                clip: true

                Text {
                    id: notesText
                    width: parent.width
                    text: updateViewModel ? updateViewModel.releaseNotes : ""
                    textFormat: Text.PlainText
                    font.pixelSize: 12
                    color: themeBridge.textMuted
                    wrapMode: Text.Wrap
                }
            }

            AppProgressBar {
                Layout.fillWidth: true
                visible: root.st === "downloading"
                value: updateViewModel ? updateViewModel.downloadProgress : 0
                showLabel: true
            }

            BusyIndicator {
                Layout.alignment: Qt.AlignHCenter
                running: root.st === "checking" || root.st === "installing" || root.st === "waiting"
                visible: running
            }

            Flow {
                Layout.fillWidth: true
                layoutDirection: Qt.RightToLeft
                spacing: Theme.spacing.sm

                AppButton {
                    visible: root.st === "available"
                    text: i18nBridge.tr("update_action_now", "Güncelle")
                    btnVariant: "primary"
                    onClicked: updateViewModel.startUpdate()
                }

                AppButton {
                    visible: root.st === "available"
                    text: i18nBridge.tr("update_action_skip", "Bu Sürümü Atla")
                    btnVariant: "secondary"
                    onClicked: updateViewModel.skipVersion()
                }

                AppButton {
                    visible: root.st === "waiting"
                    text: i18nBridge.tr("update_action_stop_waiting", "Beklemeyi Bırak")
                    btnVariant: "secondary"
                    onClicked: updateViewModel.stopWaitingForBlock()
                }

                AppButton {
                    visible: root.st === "blocked" || root.st === "error"
                    text: i18nBridge.tr("update_action_release_page", "Sürüm Sayfası")
                    btnVariant: "secondary"
                    onClicked: updateViewModel.openReleasePage()
                }

                AppButton {
                    visible: !root.isBusy
                    text: root.st === "available"
                        ? i18nBridge.tr("update_action_later", "Sonra")
                        : i18nBridge.tr("update_action_close", "Kapat")
                    btnVariant: "secondary"
                    onClicked: updateViewModel.dismiss()
                }
            }
        }
    }
}
