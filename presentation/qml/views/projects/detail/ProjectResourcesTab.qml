import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../../components"
import "../../../theme"

// Kaynaklar sekmesi.
ColumnLayout {
    id: root

    signal addRequested()
    signal editRequested(var item)

    spacing: 8

    RowLayout {
        Layout.fillWidth: true
        Text {
            text: i18nBridge.tr("tab_resources", "Proje Kaynakları:")
            font.pixelSize: 13
            color: themeBridge.textSecondary
            Layout.fillWidth: true
        }

        AppButton {
            btnVariant: "primary"
            iconName: "plus"
            text: i18nBridge.tr("action_add_resource", "Kaynak Ekle")
            implicitHeight: 28
            onClicked: root.addRequested()
        }
    }

    ScrollView {
        id: resourcesScroll
        Layout.fillWidth: true
        Layout.fillHeight: true
        clip: true

        ScrollBar.vertical: AppScrollBar { }

        ColumnLayout {
            width: resourcesScroll.availableWidth - 14
            spacing: 8

            Repeater {
                model: projectSubitemsViewModel.selectedResources
                delegate: Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: resourceContentCol.implicitHeight + 16
                    radius: 8
                    color: themeBridge.surfaceAlt
                    border.color: themeBridge.border
                    border.width: 1

                    ColumnLayout {
                        id: resourceContentCol
                        anchors.fill: parent
                        anchors.margins: 8
                        spacing: 6

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            AppBadge {
                                text: {
                                    var rt = (modelData.resource_type || "DOCUMENT").toUpperCase();
                                    switch (rt) {
                                        case "DOCUMENT": return i18nBridge.tr("resource_type_document", "Doküman");
                                        case "ARTICLE": return i18nBridge.tr("resource_type_article", "Makale");
                                        case "VIDEO": return i18nBridge.tr("resource_type_video", "Video");
                                        case "GITHUB": case "REPO": return i18nBridge.tr("resource_type_github", "GitHub / Repo");
                                        case "DESIGN": return i18nBridge.tr("resource_type_design", "Tasarım");
                                        case "API": return i18nBridge.tr("resource_type_api", "API Referansı");
                                        case "TOOL": return i18nBridge.tr("resource_type_tool", "Araç");
                                        case "OTHER": return i18nBridge.tr("resource_type_other", "Diğer");
                                        default: return modelData.resource_type;
                                    }
                                }
                                variant: "neutral"
                                size: "sm"
                            }

                            Text {
                                text: modelData.title || ""
                                font.pixelSize: 12
                                font.weight: Font.DemiBold
                                color: themeBridge.textPrimary
                                Layout.fillWidth: true
                                wrapMode: Text.Wrap
                            }

                            AppButton {
                                iconName: "external-link"
                                btnVariant: "secondary"
                                implicitWidth: 22
                                implicitHeight: 22
                                onClicked: projectSubitemsViewModel.openUrlOrPath(modelData.url)
                            }

                            AppButton {
                                iconName: "pencil"
                                btnVariant: "secondary"
                                implicitWidth: 22
                                implicitHeight: 22
                                onClicked: root.editRequested(modelData)
                            }

                            AppButton {
                                iconName: "trash-2"
                                btnVariant: "secondary"
                                implicitWidth: 22
                                implicitHeight: 22
                                onClicked: projectSubitemsViewModel.deleteResource(modelData.id)
                            }
                        }

                        Text {
                            visible: !!modelData.url
                            text: modelData.url || ""
                            font.pixelSize: 11
                            color: Theme.accent(themeBridge.currentTheme)
                            Layout.fillWidth: true
                            wrapMode: Text.WrapAnywhere
                        }
                    }
                }
            }

            Text {
                visible: !projectSubitemsViewModel.selectedResources || projectSubitemsViewModel.selectedResources.length === 0
                text: i18nBridge.tr("no_resources", "Henüz kayıtlı kaynak yok.")
                font.pixelSize: 12
                color: themeBridge.textMuted
            }
        }
    }
}
