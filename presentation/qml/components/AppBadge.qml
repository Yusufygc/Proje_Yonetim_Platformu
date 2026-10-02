import QtQuick 2.15

Rectangle {
    id: badgeRoot

    property string text: ""
    property color badgeColor: themeBridge.accentStart
    property color textColor: themeBridge.iconOnAccent

    implicitWidth: badgeText.implicitWidth + 16
    implicitHeight: 22
    radius: 999
    color: Qt.rgba(badgeColor.r, badgeColor.g, badgeColor.b, 0.2)
    border.width: 1
    border.color: Qt.rgba(badgeColor.r, badgeColor.g, badgeColor.b, 0.4)

    Text {
        id: badgeText
        anchors.centerIn: parent
        text: badgeRoot.text
        font.pixelSize: 11
        font.weight: Font.DemiBold
        color: badgeRoot.textColor
    }
}
