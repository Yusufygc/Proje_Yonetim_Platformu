import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../../components"
import "../../../theme"

// Not ekleme/düzenleme modalı.
Rectangle {
    id: root

    // Modalın bağlanacağı üst öğe (tüm ekranı kaplaması için panelin dışındaki kök)
    property Item host: null
    objectName: "addNoteDialog"
    parent: root.host
    anchors.fill: parent
    color: Qt.rgba(0, 0, 0, 0.65)
    visible: false
    z: 9999

    // editId 0 ise yeni kayıt, değilse düzenleme modu
    property int editId: 0

    function open(existing) {
        editId = existing ? existing.id : 0;
        noteTitleInput.text = existing ? existing.title : "";
        noteBodyInput.text = existing ? existing.body : "";
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
        id: noteCard
        width: Math.min(500, parent.width - 48)
        height: Math.min(noteCol.implicitHeight + noteCard.padding * 2, parent.height - 48)
        anchors.centerIn: parent
        padding: Theme.spacing.xl

        ColumnLayout {
            id: noteCol
            width: parent.width
            spacing: Theme.spacing.md

            // Başlık Çubuğu
            RowLayout {
                Layout.fillWidth: true
                spacing: Theme.spacing.sm

                AppIcon {
                    name: "note-sticky"
                    size: 20
                    color: Theme.accent(themeBridge.currentTheme)
                }

                Text {
                    text: root.editId !== 0
                          ? i18nBridge.tr("note_dialog_edit_title", "Notu Düzenle")
                          : i18nBridge.tr("note_dialog_new_title", "Yeni Proje Notu Ekle")
                    font.pixelSize: Theme.typography.sizeH3
                    font.weight: Theme.typography.weightBold
                    color: themeBridge.color("text_primary")
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
                color: themeBridge.color("border")
            }

            AppTextInput {
                id: noteTitleInput
                label: i18nBridge.tr("note_dialog_title_label", "Not Başlığı *")
                placeholder: i18nBridge.tr("note_title_placeholder", "Örn: Toplantı Notu")
                Layout.fillWidth: true
                showVoiceInput: true
            }

            AppTextInput {
                id: noteBodyInput
                label: i18nBridge.tr("note_dialog_body_label", "Not İçeriği")
                placeholder: i18nBridge.tr("note_body_placeholder", "Not içeriği...")
                isTextArea: true
                inputHeight: 100
                Layout.fillWidth: true
                showVoiceInput: true
            }

            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: themeBridge.color("border")
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
                    text: root.editId !== 0 ? i18nBridge.tr("action_save", "Kaydet") : i18nBridge.tr("action_add", "Ekle")
                    implicitWidth: 120
                    implicitHeight: 40
                    onClicked: {
                        if (noteTitleInput.text.trim() && noteBodyInput.text.trim()) {
                            if (root.editId !== 0)
                                projectSubitemsViewModel.updateNote(root.editId, noteTitleInput.text, noteBodyInput.text.trim());
                            else
                                projectSubitemsViewModel.createNote(noteTitleInput.text.trim(), noteBodyInput.text.trim());
                            root.close();
                        }
                    }
                }
            }
        }
    }
}
