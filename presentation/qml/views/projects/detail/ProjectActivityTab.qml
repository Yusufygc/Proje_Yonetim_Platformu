import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../../components"
import "../../../theme"

// Etkinlik geçmişi sekmesi.
ColumnLayout {
    id: root

    spacing: 8

    Text {
        text: i18nBridge.tr("tab_activity_title", "Son Etkinlikler:")
        font.pixelSize: 13
        color: themeBridge.color("text_secondary")
        Layout.fillWidth: true
    }

    ScrollView {
        id: activityScroll
        Layout.fillWidth: true
        Layout.fillHeight: true
        clip: true

        ScrollBar.vertical: AppScrollBar { }

        ColumnLayout {
            width: activityScroll.availableWidth - 14
            spacing: 6

            Repeater {
                model: projectSubitemsViewModel.selectedActivity
                delegate: Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: activityRow.implicitHeight + 14
                    radius: 8
                    color: themeBridge.color("surface_alt")
                    border.color: themeBridge.color("border")
                    border.width: 1

                    RowLayout {
                        id: activityRow
                        anchors.margins: 7
                        spacing: 10

                        Text {
                            text: modelData.summary
                            font.pixelSize: 12
                            color: themeBridge.color("text_primary")
                            Layout.fillWidth: true
                            wrapMode: Text.Wrap
                        }

                        Text {
                            text: modelData.created_at
                            font.pixelSize: 11
                            color: themeBridge.color("text_muted")
                        }
                    }
                }
            }

            Text {
                visible: !projectSubitemsViewModel.selectedActivity || projectSubitemsViewModel.selectedActivity.length === 0
                text: i18nBridge.tr("no_activity", "Henüz kayıtlı etkinlik yok.")
                font.pixelSize: 12
                color: themeBridge.color("text_muted")
            }
        }
    }
}
