import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../components"

// Tek değerli ölçüt kartı; genişliği kullanan yer belirler.
AppCard {
    id: root

    property string label: ""
    property string value: ""
    property string description: ""
    property color valueColor: themeBridge.accentStart
    property int valueSize: 24

    height: 100

    Column {
        anchors.centerIn: parent
        spacing: 4

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: root.label
            font.pixelSize: 12
            color: themeBridge.textSecondary
        }
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: root.value
            font.pixelSize: root.valueSize
            font.weight: Font.Bold
            color: root.valueColor
            elide: Text.ElideRight
        }
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: root.description
            font.pixelSize: 11
            color: themeBridge.textMuted
        }
    }
}
