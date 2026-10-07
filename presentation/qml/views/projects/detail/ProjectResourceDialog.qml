import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../../components"
import "../../../theme"

// Kaynak ekleme/düzenleme modalı.
Rectangle {
    id: root

    // Modalın bağlanacağı üst öğe (tüm ekranı kaplaması için panelin dışındaki kök)
    property Item host: null
    objectName: "addResourceDialog"
    parent: root.host
    anchors.fill: parent
    color: Qt.rgba(0, 0, 0, 0.65)
    visible: false
    z: 9999

    // editId 0 ise yeni kayıt, değilse düzenleme modu
    property int editId: 0

    function open(existing) {
        editId = existing ? existing.id : 0;
        resourceTitleInput.text = existing ? existing.title : "";
        resourceUrlInput.text = existing ? existing.url : "";
        resourceTypeCombo.selectedValue = existing ? existing.resource_type : "DOCUMENT";
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
        id: resourceCard
        width: Math.min(500, parent.width - 48)
        height: Math.min(resourceCol.implicitHeight + resourceCard.padding * 2, parent.height - 48)
        anchors.centerIn: parent
        padding: Theme.spacing.xl

        ColumnLayout {
            id: resourceCol
            width: parent.width
            spacing: Theme.spacing.md

            // Başlık Çubuğu
            RowLayout {
                Layout.fillWidth: true
                spacing: Theme.spacing.sm

                AppIcon {
                    name: "external-link"
                    size: 20
                    color: Theme.accent(themeBridge.currentTheme)
                }

                Text {
                    text: root.editId !== 0
                          ? i18nBridge.tr("resource_dialog_edit_title", "Kaynağı Düzenle")
                          : i18nBridge.tr("resource_dialog_new_title", "Yeni Kaynak Ekle")
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
                id: resourceTitleInput
                label: i18nBridge.tr("resource_dialog_title_label", "Kaynak Adı *")
                placeholder: i18nBridge.tr("resource_title_placeholder", "Örn: API Dokümantasyonu")
                Layout.fillWidth: true
                showVoiceInput: true
            }

            AppTextInput {
                id: resourceUrlInput
                label: i18nBridge.tr("resource_dialog_url_label", "Kaynak Bağlantısı (URL / Yol) *")
                placeholder: i18nBridge.tr("resource_url_placeholder", "https://api.example.com veya dosya yolu")
                Layout.fillWidth: true
            }

            AppComboBox {
                id: resourceTypeCombo
                label: i18nBridge.tr("field_resource_type", "Kaynak Türü")
                Layout.fillWidth: true
                model: [
                    { "text": i18nBridge.tr("resource_type_document", "Doküman"), "value": "DOCUMENT" },
                    { "text": i18nBridge.tr("resource_type_article", "Makale"), "value": "ARTICLE" },
                    { "text": i18nBridge.tr("resource_type_video", "Video"), "value": "VIDEO" },
                    { "text": i18nBridge.tr("resource_type_github", "GitHub / Repo"), "value": "GITHUB" },
                    { "text": i18nBridge.tr("resource_type_design", "Tasarım"), "value": "DESIGN" },
                    { "text": i18nBridge.tr("resource_type_api", "API Referansı"), "value": "API" },
                    { "text": i18nBridge.tr("resource_type_tool", "Araç"), "value": "TOOL" },
                    { "text": i18nBridge.tr("resource_type_other", "Diğer"), "value": "OTHER" }
                ]
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
                        if (resourceTitleInput.text.trim() && resourceUrlInput.text.trim()) {
                            var rType = resourceTypeCombo.selectedValue || "DOCUMENT";
                            if (root.editId !== 0)
                                projectSubitemsViewModel.updateResource(root.editId, resourceTitleInput.text, resourceUrlInput.text, rType);
                            else
                                projectSubitemsViewModel.createResource(resourceTitleInput.text.trim(), resourceUrlInput.text.trim(), rType);
                            root.close();
                        }
                    }
                }
            }
        }
    }
}
