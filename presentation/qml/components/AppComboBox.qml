import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"

Column {
    id: root

    property string label: ""
    property var model: []
    property int currentIndex: 0
    property string currentValue: model && model.length > currentIndex ? model[currentIndex] : ""

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
        id: selectorBox
        width: parent.width
        height: 38
        radius: 8
        color: themeBridge.background
        border.width: 1
        border.color: comboMouse.containsMouse || menuPopup.opened ? themeBridge.accentStart : themeBridge.border

        Row {
            anchors.fill: parent
            anchors.leftMargin: 12
            anchors.rightMargin: 12
            spacing: 8

            Text {
                width: parent.width - 24
                text: root.currentValue
                font.pixelSize: 13
                color: themeBridge.textPrimary
                anchors.verticalCenter: parent.verticalCenter
                elide: Text.ElideRight
            }

            Text {
                text: "▼"
                font.pixelSize: 10
                color: themeBridge.textMuted
                anchors.verticalCenter: parent.verticalCenter
            }
        }

        MouseArea {
            id: comboMouse
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: menuPopup.open()
        }

        Menu {
            id: menuPopup
            y: selectorBox.height + 4
            width: selectorBox.width

            background: Rectangle {
                radius: 8
                color: themeBridge.surface
                border.width: 1
                border.color: themeBridge.border
            }

            Repeater {
                model: root.model
                MenuItem {
                    text: modelData
                    onTriggered: {
                        root.currentIndex = index;
                    }
                }
            }
        }
    }
}
