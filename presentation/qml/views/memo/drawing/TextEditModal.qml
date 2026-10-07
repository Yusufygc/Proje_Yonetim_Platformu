import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../../components"
import "../../../theme"

// Blok metni veya ok etiketi düzenleme penceresi; tuval alanının üstünü kaplar.
Item {
    id: modal

    property bool active: false

    signal applied(string text)
    signal canceled()

    anchors.fill: parent
    visible: active
    z: 99

    function open(title, text) {
        modalTitleText.text = title
        blockTextInput.text = text
    }

    Rectangle {
        anchors.fill: parent
        color: "#40000000"

        MouseArea {
            anchors.fill: parent
            onClicked: modal.applied(blockTextInput.text)
        }
    }

    Rectangle {
        anchors.centerIn: parent
        width: Math.min(360, parent.width - 32)
        height: 146
        radius: Theme.radius.medium
        color: themeBridge.isDark ? "#24242A" : "#FFFFFF"
        border.color: Theme.accent(themeBridge.currentTheme)
        border.width: 1.5

        MouseArea {
            anchors.fill: parent
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: Theme.spacing.md
            spacing: Theme.spacing.sm

            Text {
                id: modalTitleText
                text: i18nBridge.tr("title_edit_block_text", "Blok Metnini Düzenle")
                font.pixelSize: Theme.typography.sizeBody
                font.weight: Font.Medium
                color: themeBridge.textPrimary
            }

            AppTextInput {
                id: blockTextInput
                Layout.fillWidth: true
                placeholder: i18nBridge.tr("placeholder_block_text", "Metin girin...")
                showVoiceInput: true
                onAccepted: modal.applied(blockTextInput.text)
            }

            RowLayout {
                Layout.alignment: Qt.AlignRight
                spacing: Theme.spacing.xs

                AppButton {
                    text: i18nBridge.tr("action_cancel", "İptal")
                    btnVariant: "secondary"
                    implicitHeight: 28
                    onClicked: modal.canceled()
                }

                AppButton {
                    text: i18nBridge.tr("action_save", "Tamam")
                    btnVariant: "primary"
                    implicitHeight: 28
                    onClicked: modal.applied(blockTextInput.text)
                }
            }
        }
    }
}
