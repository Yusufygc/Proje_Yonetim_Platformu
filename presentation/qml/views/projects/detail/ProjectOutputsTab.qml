import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../../components"
import "../../../theme"

// Çıktılar sekmesi.
ColumnLayout {
    id: root

    signal addRequested()

    spacing: 8

    RowLayout {
        Layout.fillWidth: true
        Text {
            text: i18nBridge.tr("tab_outputs", "Proje Çıktıları ve Ekleri:")
            font.pixelSize: 13
            color: themeBridge.textSecondary
            Layout.fillWidth: true
        }

        AppButton {
            btnVariant: "primary"
            iconName: "plus"
            text: i18nBridge.tr("action_add_output", "Çıktı Ekle")
            implicitHeight: 28
            onClicked: root.addRequested()
        }
    }

    ScrollView {
        id: outputsScroll
        Layout.fillWidth: true
        Layout.fillHeight: true
        clip: true

        ScrollBar.vertical: AppScrollBar { }

        ColumnLayout {
            width: outputsScroll.availableWidth - 14
            spacing: 8

            Repeater {
                model: projectSubitemsViewModel.selectedOutputs
                delegate: Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: outputContentCol.implicitHeight + 16
                    radius: 8
                    color: themeBridge.surfaceAlt
                    border.color: themeBridge.border
                    border.width: 1

                    ColumnLayout {
                        id: outputContentCol
                        anchors.fill: parent
                        anchors.margins: 8
                        spacing: 6

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            AppIcon {
                                name: "paperclip"
                                size: 14
                                color: themeBridge.textMuted
                                Layout.alignment: Qt.AlignVCenter
                            }

                            Text {
                                text: modelData.title
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
                                onClicked: projectSubitemsViewModel.openUrlOrPath(modelData.file_path)
                            }
                        }

                        Text {
                            visible: !!modelData.file_path
                            text: modelData.file_path || ""
                            font.pixelSize: 11
                            color: themeBridge.textMuted
                            Layout.fillWidth: true
                            wrapMode: Text.WrapAnywhere
                        }
                    }
                }
            }

            Text {
                visible: !projectSubitemsViewModel.selectedOutputs || projectSubitemsViewModel.selectedOutputs.length === 0
                text: i18nBridge.tr("no_outputs", "Henüz kayıtlı çıktı yok.")
                font.pixelSize: 12
                color: themeBridge.textMuted
            }
        }
    }
}
