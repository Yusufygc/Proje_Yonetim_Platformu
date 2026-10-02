import QtQuick 2.15

Item {
    id: root

    property int value: 0 // 0 - 100
    property bool showLabel: false
    property int barHeight: 6
    property color barColor: value >= 100 ? themeBridge.success : themeBridge.accentStart

    implicitWidth: 100
    implicitHeight: Math.max(barHeight, showLabel ? 16 : barHeight)

    Row {
        anchors.fill: parent
        spacing: 8

        Rectangle {
            id: track
            width: root.showLabel ? parent.width - 36 : parent.width
            height: root.barHeight
            radius: root.barHeight / 2
            color: themeBridge.surfaceRaised
            anchors.verticalCenter: parent.verticalCenter

            Rectangle {
                id: fill
                height: parent.height
                radius: parent.radius
                width: Math.max(0, Math.min(track.width, track.width * (root.value / 100.0)))
                color: root.barColor

                Behavior on width {
                    NumberAnimation { duration: 250; easing.type: Easing.OutQuad }
                }
            }
        }

        Text {
            visible: root.showLabel
            text: "%" + root.value
            font.pixelSize: 11
            font.weight: Font.DemiBold
            color: themeBridge.textSecondary
            anchors.verticalCenter: parent.verticalCenter
        }
    }
}
