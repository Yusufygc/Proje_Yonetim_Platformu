import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../../components"
import "../../../theme"

// Kararlar sekmesi.
ColumnLayout {
    id: root

    signal addRequested()
    signal editRequested(var item)

    spacing: 8

    RowLayout {
        Layout.fillWidth: true
        Text {
            text: i18nBridge.tr("tab_decisions", "Proje Kararları:")
            font.pixelSize: 13
            color: themeBridge.color("text_secondary")
            Layout.fillWidth: true
        }

        AppButton {
            btnVariant: "primary"
            iconName: "plus"
            text: i18nBridge.tr("action_add_decision", "Karar Ekle")
            implicitHeight: 28
            onClicked: root.addRequested()
        }
    }

    ScrollView {
        id: decisionsScroll
        Layout.fillWidth: true
        Layout.fillHeight: true
        clip: true

        ScrollBar.vertical: AppScrollBar { }

        ColumnLayout {
            width: decisionsScroll.availableWidth - 14
            spacing: 8

            Repeater {
                model: projectSubitemsViewModel.selectedDecisions
                delegate: Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: decisionContentCol.implicitHeight + 16
                    radius: 8
                    color: themeBridge.color("surface_alt")
                    border.color: themeBridge.color("border")
                    border.width: 1

                    ColumnLayout {
                        id: decisionContentCol
                        anchors.fill: parent
                        anchors.margins: 8
                        spacing: 6

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            AppBadge {
                                text: {
                                    switch (modelData.status) {
                                        case "ACCEPTED": return i18nBridge.tr("decision_status_accepted", "Kabul Edildi");
                                        case "DRAFT": return i18nBridge.tr("decision_status_draft", "Taslak");
                                        case "SUPERSEDED": return i18nBridge.tr("decision_status_superseded", "Güncellendi");
                                        case "CANCELLED": return i18nBridge.tr("decision_status_cancelled", "İptal Edildi");
                                        default: return modelData.status;
                                    }
                                }
                                variant: {
                                    switch (modelData.status) {
                                        case "ACCEPTED": return "success";
                                        case "CANCELLED": return "danger";
                                        case "SUPERSEDED": return "warning";
                                        default: return "neutral";
                                    }
                                }
                                size: "sm"
                            }

                            Text {
                                text: modelData.title || ""
                                font.pixelSize: 12
                                font.weight: Font.DemiBold
                                color: themeBridge.color("text_primary")
                                Layout.fillWidth: true
                                wrapMode: Text.Wrap
                            }

                            AppButton {
                                iconName: "pencil"
                                btnVariant: "secondary"
                                implicitWidth: 22
                                implicitHeight: 22
                                Layout.alignment: Qt.AlignTop
                                onClicked: root.editRequested(modelData)
                            }

                            // Backend karar silmez, "İptal Edildi" durumuna alır
                            AppButton {
                                iconName: "x"
                                btnVariant: "secondary"
                                implicitWidth: 22
                                implicitHeight: 22
                                visible: modelData.status !== "CANCELLED"
                                Layout.alignment: Qt.AlignTop
                                onClicked: projectSubitemsViewModel.deleteDecision(modelData.id)
                            }
                        }

                        Text {
                            visible: !!modelData.decision
                            text: modelData.decision || ""
                            font.pixelSize: 12
                            color: themeBridge.color("text_secondary")
                            Layout.fillWidth: true
                            wrapMode: Text.Wrap
                        }
                    }
                }
            }

            Text {
                visible: !projectSubitemsViewModel.selectedDecisions || projectSubitemsViewModel.selectedDecisions.length === 0
                text: i18nBridge.tr("no_decisions", "Henüz kayıtlı karar yok.")
                font.pixelSize: 12
                color: themeBridge.color("text_muted")
            }
        }
    }
}
