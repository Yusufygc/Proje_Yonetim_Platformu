import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Column {
    id: root

    property string label: ""
    property alias text: inputField.text
    property string placeholder: ""
    property bool isTextArea: false
    property bool readOnly: false
    property bool showVoiceInput: false
    property int inputHeight: isTextArea ? 80 : 38

    signal accepted()

    Layout.fillWidth: true
    width: parent ? parent.width : 200
    spacing: 6

    Text {
        visible: root.label !== ""
        text: root.label
        font.pixelSize: 12
        font.weight: Font.Medium
        color: themeBridge.textSecondary
    }

    Rectangle {
        width: parent.width
        height: root.inputHeight
        radius: 8
        color: themeBridge.background
        border.width: 1
        border.color: inputField.activeFocus ? themeBridge.accentStart : themeBridge.border

        Behavior on border.color { ColorAnimation { duration: 150 } }

        Flickable {
            id: flickableArea
            anchors.fill: parent
            anchors.leftMargin: 10
            anchors.rightMargin: (root.showVoiceInput && !root.readOnly) ? 38 : 10
            anchors.topMargin: 10
            anchors.bottomMargin: 10
            contentWidth: inputField.paintedWidth
            contentHeight: inputField.paintedHeight
            clip: true
            interactive: root.isTextArea

            TextEdit {
                id: inputField
                width: flickableArea.width
                font.pixelSize: 13
                color: themeBridge.textPrimary
                readOnly: root.readOnly
                selectByMouse: true
                wrapMode: root.isTextArea ? TextEdit.Wrap : TextEdit.NoWrap

                Keys.onReturnPressed: function(event) {
                    if (!root.isTextArea) {
                        root.accepted();
                        event.accepted = true;
                    }
                }
                Keys.onEnterPressed: function(event) {
                    if (!root.isTextArea) {
                        root.accepted();
                        event.accepted = true;
                    }
                }

                Text {
                    anchors.fill: parent
                    text: root.placeholder
                    color: themeBridge.textMuted
                    font.pixelSize: 13
                    visible: !inputField.text && !inputField.activeFocus
                }
            }
        }

        VoiceInputButton {
            anchors.right: parent.right
            anchors.rightMargin: 4
            anchors.verticalCenter: root.isTextArea ? undefined : parent.verticalCenter
            anchors.top: root.isTextArea ? parent.top : undefined
            anchors.topMargin: root.isTextArea ? 4 : 0
            visible: root.showVoiceInput && !root.readOnly
            target: inputField
        }
    }
}
