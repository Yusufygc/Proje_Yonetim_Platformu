import QtQuick 2.15

Rectangle {
    id: cardRoot
    default property alias content: innerContainer.data
    property int padding: 16
    property bool hoverable: false
    property bool isHovered: hoverArea.containsMouse

    radius: 12
    color: isHovered && hoverable ? themeBridge.surfaceRaised : themeBridge.surface
    border.width: 1
    border.color: isHovered && hoverable ? themeBridge.accentStart : themeBridge.border

    Behavior on color { ColorAnimation { duration: 150 } }
    Behavior on border.color { ColorAnimation { duration: 150 } }

    MouseArea {
        id: hoverArea
        anchors.fill: parent
        hoverEnabled: cardRoot.hoverable
        acceptedButtons: Qt.NoButton
    }

    Item {
        id: innerContainer
        anchors.fill: parent
        anchors.margins: cardRoot.padding
    }
}
