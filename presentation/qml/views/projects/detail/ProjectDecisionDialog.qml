import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../../components"
import "../../../theme"

// Karar ekleme/düzenleme modalı.
Rectangle {
    id: root

    // Modalın bağlanacağı üst öğe (tüm ekranı kaplaması için panelin dışındaki kök)
    property Item host: null
    objectName: "addDecisionDialog"
    parent: root.host
    anchors.fill: parent
    color: Qt.rgba(0, 0, 0, 0.65)
    visible: false
    z: 9999

    // editId 0 ise yeni kayıt, değilse düzenleme modu
    property int editId: 0

    function open(existing) {
        editId = existing ? existing.id : 0;
        decisionTitleInput.text = existing ? existing.title : "";
        decisionTextInput.text = existing ? existing.decision : "";
        decisionStatusCombo.selectedValue = existing ? existing.status : "ACCEPTED";
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
        id: decisionCard
        width: Math.min(500, parent.width - 48)
        height: Math.min(decisionCol.implicitHeight + decisionCard.padding * 2, parent.height - 48)
        anchors.centerIn: parent
        padding: Theme.spacing.xl

        ColumnLayout {
            id: decisionCol
            width: parent.width
            spacing: Theme.spacing.md

            // Başlık Çubuğu
            RowLayout {
                Layout.fillWidth: true
                spacing: Theme.spacing.sm

                AppIcon {
                    name: "check_square"
                    size: 20
                    color: Theme.accent(themeBridge.currentTheme)
                }

                Text {
                    text: root.editId !== 0
                          ? i18nBridge.tr("decision_dialog_edit_title", "Kararı Düzenle")
                          : i18nBridge.tr("decision_dialog_new_title", "Yeni Karar Ekle")
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
                id: decisionTitleInput
                label: i18nBridge.tr("decision_dialog_title_label", "Karar Konusu *")
                placeholder: i18nBridge.tr("decision_title_placeholder", "Örn: Mimari Seçim Kararı")
                Layout.fillWidth: true
                showVoiceInput: true
            }

            AppTextInput {
                id: decisionTextInput
                label: i18nBridge.tr("decision_dialog_decision_label", "Alınan Karar *")
                placeholder: i18nBridge.tr("decision_desc_placeholder", "Detaylı karar açıklaması...")
                isTextArea: true
                inputHeight: 80
                Layout.fillWidth: true
                showVoiceInput: true
            }

            AppComboBox {
                id: decisionStatusCombo
                label: i18nBridge.tr("field_status", "Durum")
                Layout.fillWidth: true
                model: [
                    { "text": i18nBridge.tr("decision_status_accepted", "Kabul Edildi"), "value": "ACCEPTED" },
                    { "text": i18nBridge.tr("decision_status_draft", "Taslak"), "value": "DRAFT" },
                    { "text": i18nBridge.tr("decision_status_superseded", "Güncellendi"), "value": "SUPERSEDED" },
                    { "text": i18nBridge.tr("decision_status_cancelled", "İptal Edildi"), "value": "CANCELLED" }
                ]
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
                    text: root.editId !== 0 ? i18nBridge.tr("action_save", "Kaydet") : i18nBridge.tr("action_add", "Ekle")
                    implicitWidth: 120
                    implicitHeight: 40
                    onClicked: {
                        if (decisionTitleInput.text.trim() && decisionTextInput.text.trim()) {
                            var st = decisionStatusCombo.selectedValue || "ACCEPTED";
                            if (root.editId !== 0)
                                projectSubitemsViewModel.updateDecision(root.editId, decisionTitleInput.text, decisionTextInput.text, st);
                            else
                                projectSubitemsViewModel.createDecision(decisionTitleInput.text.trim(), decisionTextInput.text.trim(), st);
                            root.close();
                        }
                    }
                }
            }
        }
    }
}
