import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../../components"
import "../../../theme"

// Çıktı ekleme modalı.
Rectangle {
    id: root

    // Modalın bağlanacağı üst öğe (tüm ekranı kaplaması için panelin dışındaki kök)
    property Item host: null
    objectName: "addOutputDialog"
    parent: root.host
    anchors.fill: parent
    color: Qt.rgba(0, 0, 0, 0.65)
    visible: false
    z: 9999

    function open() {
        outputTitleInput.text = "";
        outputPathInput.text = "";
        visible = true;
    }

    function close() {
        visible = false;
    }

    MouseArea {
        anchors.fill: parent
        onClicked: { /* modal dışı tıklamayı engeller */ }
    }

    Shortcut {
        sequence: "Escape"
        enabled: root.visible
        onActivated: root.close()
    }

    AppCard {
        id: outputCard
        width: Math.min(480, parent.width - 48)
        height: Math.min(outputCol.implicitHeight + outputCard.padding * 2, parent.height - 48)
        anchors.centerIn: parent
        padding: Theme.spacing.xl

        ColumnLayout {
            id: outputCol
            width: parent.width
            spacing: Theme.spacing.md

            // Başlık Çubuğu
            RowLayout {
                Layout.fillWidth: true
                spacing: Theme.spacing.sm

                AppIcon {
                    name: "copy"
                    size: 20
                    color: Theme.accent(themeBridge.currentTheme)
                }

                Text {
                    text: i18nBridge.tr("dialog_add_output_title", "Yeni Çıktı Ekle")
                    font.pixelSize: Theme.typography.sizeH3
                    font.weight: Theme.typography.weightBold
                    color: themeBridge.textPrimary
                    Layout.fillWidth: true
                }

                AppButton {
                    iconName: "x"
                    btnVariant: "secondary"
                    implicitWidth: 32
                    implicitHeight: 32
                    onClicked: root.close()
                }
            }

            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: themeBridge.border
            }

            AppTextInput {
                id: outputTitleInput
                label: i18nBridge.tr("field_output_title", "Çıktı Başlığı *")
                placeholder: i18nBridge.tr("output_title_placeholder", "Rapor, doküman veya dosya adı")
                Layout.fillWidth: true
                showVoiceInput: true
            }

            AppTextInput {
                id: outputPathInput
                label: i18nBridge.tr("field_output_path", "Dosya Yolu / URL")
                placeholder: i18nBridge.tr("output_path_placeholder", "C:/docs/rapor.pdf veya https://...")
                Layout.fillWidth: true
            }

            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: themeBridge.border
            }

            // Alt Butonlar
            RowLayout {
                Layout.alignment: Qt.AlignHCenter
                spacing: Theme.spacing.md

                AppButton {
                    btnVariant: "secondary"
                    text: i18nBridge.tr("btn_cancel", "İptal")
                    implicitWidth: 120
                    implicitHeight: 40
                    onClicked: root.close()
                }

                AppButton {
                    btnVariant: "primary"
                    text: i18nBridge.tr("action_add", "Ekle")
                    implicitWidth: 120
                    implicitHeight: 40
                    onClicked: {
                        if (outputTitleInput.text.trim()) {
                            projectSubitemsViewModel.addOutput(outputTitleInput.text.trim(), outputPathInput.text.trim());
                            root.close();
                        }
                    }
                }
            }
        }
    }
}
