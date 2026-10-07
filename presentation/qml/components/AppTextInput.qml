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
            anchors.topMargin: root.isTextArea ? 8 : 0
            anchors.bottomMargin: root.isTextArea ? 8 : 0
            contentWidth: root.isTextArea ? flickableArea.width : Math.max(flickableArea.width, inputField.paintedWidth + 12)
            contentHeight: root.isTextArea ? Math.max(flickableArea.height, inputField.paintedHeight) : flickableArea.height
            clip: true
            interactive: root.isTextArea
            boundsBehavior: Flickable.StopAtBounds

            ScrollBar.vertical: AppScrollBar {
                visible: root.isTextArea && flickableArea.contentHeight > flickableArea.height
            }

            function ensureVisible(rect) {
                var margin = 16
                if (!root.isTextArea) {
                    if (contentX > rect.x - margin) {
                        contentX = Math.max(0, rect.x - margin)
                    } else if (contentX + width < rect.x + rect.width + margin) {
                        contentX = Math.min(Math.max(0, contentWidth - width), rect.x + rect.width + margin - width)
                    }
                } else {
                    if (contentY > rect.y - margin) {
                        contentY = Math.max(0, rect.y - margin)
                    } else if (contentY + height < rect.y + rect.height + margin) {
                        contentY = Math.min(Math.max(0, contentHeight - height), rect.y + rect.height + margin - height)
                    }
                }
            }

            WheelHandler {
                enabled: !root.isTextArea && (flickableArea.contentWidth > flickableArea.width)
                orientation: Qt.Horizontal | Qt.Vertical
                onWheel: function(event) {
                    var delta = (event.angleDelta.y !== 0 ? event.angleDelta.y : event.angleDelta.x)
                    flickableArea.contentX = Math.max(0, Math.min(flickableArea.contentWidth - flickableArea.width, flickableArea.contentX - delta))
                }
            }

            TextEdit {
                id: inputField
                width: root.isTextArea ? flickableArea.width : Math.max(flickableArea.width, paintedWidth + 12)
                height: root.isTextArea ? Math.max(flickableArea.height, paintedHeight) : flickableArea.height
                verticalAlignment: root.isTextArea ? TextEdit.AlignTop : TextEdit.AlignVCenter
                font.pixelSize: 13
                color: themeBridge.textPrimary
                readOnly: root.readOnly
                selectByMouse: true
                wrapMode: root.isTextArea ? TextEdit.Wrap : TextEdit.NoWrap

                onCursorRectangleChanged: {
                    flickableArea.ensureVisible(cursorRectangle)
                }

                onActiveFocusChanged: {
                    if (!activeFocus && !root.isTextArea) {
                        flickableArea.contentX = 0
                    }
                }

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
                    verticalAlignment: root.isTextArea ? Text.AlignTop : Text.AlignVCenter
                    text: root.placeholder
                    color: themeBridge.textMuted
                    font.pixelSize: 13
                    wrapMode: root.isTextArea ? Text.Wrap : Text.NoWrap
                    elide: root.isTextArea ? Text.ElideNone : Text.ElideRight
                    visible: !inputField.text && !inputField.activeFocus
                }
            }
        }

        MouseArea {
            id: hoverTooltipArea
            anchors.fill: flickableArea
            hoverEnabled: true
            acceptedButtons: Qt.NoButton

            ToolTip.visible: hoverTooltipArea.containsMouse && !inputField.activeFocus && (inputField.paintedWidth > flickableArea.width)
            ToolTip.text: inputField.text
            ToolTip.delay: 450
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
