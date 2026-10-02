import QtQuick 2.15

Item {
    id: root
    property string name: ""
    property color color: "#FFFFFF"
    property int size: 20

    width: size
    height: size

    Image {
        id: img
        anchors.fill: parent
        source: root.name !== "" ? "image://icons/" + root.name + "?color=" + encodeURIComponent(root.color.toString()) : ""
        sourceSize.width: root.size * 2
        sourceSize.height: root.size * 2
        fillMode: Image.PreserveAspectFit
        smooth: true
        asynchronous: false
    }
}
