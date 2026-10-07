import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../../components"
import "../../../theme"

// Notlar sekmesi.
ColumnLayout {
    id: root

    signal addRequested()
    signal editRequested(var item)

    spacing: 8

    RowLayout {
        Layout.fillWidth: true
        Text {
            text: i18nBridge.tr("tab_notes", "Proje Notları:")
            font.pixelSize: 13
            color: themeBridge.color("text_secondary")
            Layout.fillWidth: true
        }

        AppButton {
            btnVariant: "primary"
            iconName: "plus"
            text: i18nBridge.tr("action_add_note", "Not Ekle")
            implicitHeight: 28
            onClicked: root.addRequested()
        }
    }

    ListView {
        id: notesListView
        Layout.fillWidth: true
        Layout.fillHeight: true
        clip: true
        spacing: 8
        model: projectSubitemsViewModel.selectedNotes

        ScrollBar.vertical: AppScrollBar { }

        delegate: Rectangle {
            width: notesListView.width - 14
            height: noteCol.implicitHeight + 20
            radius: 8
            color: themeBridge.surfaceAlt
            border.color: themeBridge.border
            border.width: 1

            Column {
                id: noteCol
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.margins: 10
                spacing: 6

                Item {
                    width: parent.width
                    implicitHeight: Math.max(noteTitleText.implicitHeight, 24)

                    Text {
                        id: noteTitleText
                        anchors.left: parent.left
                        anchors.right: noteEditBtn.left
                        anchors.rightMargin: 8
                        anchors.top: parent.top
                        visible: !!modelData.title
                        text: modelData.title || ""
                        font.pixelSize: 13
                        font.weight: Font.DemiBold
                        color: themeBridge.textPrimary
                        wrapMode: Text.Wrap
                    }

                    AppButton {
                        id: noteEditBtn
                        iconName: "pencil"
                        btnVariant: "secondary"
                        implicitWidth: 24
                        implicitHeight: 24
                        anchors.right: noteDeleteBtn.left
                        anchors.rightMargin: 4
                        anchors.top: parent.top
                        onClicked: root.editRequested(modelData)
                    }

                    AppButton {
                        id: noteDeleteBtn
                        iconName: "trash-2"
                        btnVariant: "secondary"
                        implicitWidth: 24
                        implicitHeight: 24
                        anchors.right: parent.right
                        anchors.top: parent.top
                        onClicked: projectSubitemsViewModel.deleteNote(modelData.id)
                    }
                }

                Text {
                    width: parent.width
                    visible: !!modelData.body
                    text: modelData.body || ""
                    font.pixelSize: 12
                    color: themeBridge.textSecondary
                    wrapMode: Text.Wrap
                }
            }
        }

        Text {
            anchors.centerIn: parent
            visible: !projectSubitemsViewModel.selectedNotes || projectSubitemsViewModel.selectedNotes.length === 0
            text: i18nBridge.tr("no_notes", "Henüz kayıtlı proje notu yok.")
            font.pixelSize: 12
            color: themeBridge.textMuted
        }
    }
}
