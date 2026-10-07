import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../../components"
import "../../../theme"

// Süreç aşamaları (açılır/kapanır liste).
AppCard {
    id: root
    height: stagesContentColumn.implicitHeight + 32
    clip: true

    property bool stagesExpanded: true

    Column {
        id: stagesContentColumn
        anchors.fill: parent
        spacing: 12

        // Tıklanabilir Açılır / Kapanır Başlık Satırı
        Rectangle {
            width: parent.width
            height: 32
            color: "transparent"

            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                onClicked: root.stagesExpanded = !root.stagesExpanded
            }

            RowLayout {
                anchors.fill: parent
                spacing: 8

                AppIcon {
                    name: root.stagesExpanded ? "chevron-down" : "chevron-right"
                    size: 16
                    color: themeBridge.accentStart
                    Layout.alignment: Qt.AlignVCenter
                }

                Text {
                    text: i18nBridge.tr("section_stages", "SÜREÇ AŞAMALARI")
                    font.pixelSize: 13
                    font.weight: Font.DemiBold
                    color: themeBridge.textPrimary
                    Layout.alignment: Qt.AlignVCenter
                }

                // Tamamlanan Aşama Sayacı
                Text {
                    text: {
                        var list = projectViewModel.selectedStages || [];
                        var doneCount = 0;
                        for (var i = 0; i < list.length; i++) {
                            if (list[i].status === "DONE" || list[i].status === "COMPLETED") {
                                doneCount++;
                            }
                        }
                        return "(" + doneCount + "/" + list.length + " " + i18nBridge.tr("status_completed", "Tamamlandı") + ")";
                    }
                    font.pixelSize: 12
                    color: themeBridge.textMuted
                    Layout.alignment: Qt.AlignVCenter
                }

                Item { Layout.fillWidth: true }

                Text {
                    text: root.stagesExpanded ? i18nBridge.tr("action_collapse", "Daralt") : i18nBridge.tr("action_expand", "Genişlet")
                    font.pixelSize: 11
                    color: themeBridge.accentStart
                    Layout.alignment: Qt.AlignVCenter
                }
            }
        }

        // Aşamalar Listesi (Açıkken Görünür)
        Column {
            id: stagesListColumn
            width: parent.width
            spacing: 10
            visible: root.stagesExpanded

            Repeater {
                model: projectViewModel.selectedStages
                delegate: RowLayout {
                    width: stagesListColumn.width
                    height: 36
                    spacing: 12

                    Rectangle {
                        width: 10
                        height: 10
                        radius: 5
                        color: (modelData.status === "DONE" || modelData.status === "COMPLETED") ? themeBridge.success : (
                            (modelData.status === "ACTIVE" || modelData.status === "IN_PROGRESS") ? themeBridge.accentStart : themeBridge.border
                        )
                        Layout.alignment: Qt.AlignVCenter
                    }

                    Text {
                        text: (index + 1) + ". " + modelData.name
                        font.pixelSize: 13
                        font.weight: (modelData.status === "ACTIVE" || modelData.status === "IN_PROGRESS") ? Font.DemiBold : Font.Normal
                        color: (modelData.status === "DONE" || modelData.status === "COMPLETED") ? themeBridge.textMuted : themeBridge.textPrimary
                        Layout.fillWidth: true
                        elide: Text.ElideRight
                        Layout.alignment: Qt.AlignVCenter
                    }

                    AppBadge {
                        text: {
                            var st = modelData.status;
                            if (st === "DONE" || st === "COMPLETED") return i18nBridge.tr("status_completed", "Tamamlandı");
                            if (st === "ACTIVE" || st === "IN_PROGRESS") return i18nBridge.tr("status_active", "Aktif");
                            if (st === "SKIPPED") return i18nBridge.tr("status_skipped", "Atlandı");
                            return i18nBridge.tr("status_not_started", "Başlamadı");
                        }
                        variant: {
                            var st = modelData.status;
                            if (st === "DONE" || st === "COMPLETED") return "success";
                            if (st === "ACTIVE" || st === "IN_PROGRESS") return "info";
                            return "neutral";
                        }
                        size: "sm"
                        Layout.alignment: Qt.AlignVCenter
                    }

                    AppButton {
                        visible: modelData.status !== "COMPLETED" && modelData.status !== "DONE"
                        variant: "secondary"
                        text: i18nBridge.tr("btn_complete_stage", "Tamamla")
                        implicitHeight: 28
                        onClicked: projectViewModel.completeStage(modelData.id)
                        Layout.alignment: Qt.AlignVCenter
                    }

                    AppButton {
                        visible: modelData.status === "NOT_STARTED"
                        variant: "primary"
                        text: i18nBridge.tr("btn_activate_stage", "Aktif Et")
                        implicitHeight: 28
                        onClicked: projectViewModel.activateStage(modelData.id)
                        Layout.alignment: Qt.AlignVCenter
                    }
                }
            }
        }
    }
}
