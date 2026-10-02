import QtQuick 2.15

Rectangle {
    id: toastRoot

    property string message: ""
    property string toastType: "info"
    property int duration: 3000

    implicitWidth: Math.min(500, Math.max(280, contentRow.implicitWidth + 32))
    implicitHeight: 44
    radius: 22

    color: {
        if (toastType === "success") return themeBridge.success;
        if (toastType === "danger" || toastType === "error") return themeBridge.danger;
        if (toastType === "warning") return themeBridge.warning;
        return themeBridge.accentStart;
    }

    opacity: 0.0
    visible: opacity > 0.0
    y: visible ? 24 : -50

    Behavior on opacity { NumberAnimation { duration: 250; easing.type: Easing.OutCubic } }
    Behavior on y { NumberAnimation { duration: 250; easing.type: Easing.OutCubic } }

    Timer {
        id: hideTimer
        interval: toastRoot.duration
        repeat: false
        onTriggered: {
            toastRoot.opacity = 0.0
            toastRoot.y = -50
        }
    }

    Row {
        id: contentRow
        anchors.centerIn: parent
        spacing: 10

        Text {
            id: iconText
            text: {
                if (toastRoot.toastType === "success") return "✓";
                if (toastRoot.toastType === "danger" || toastRoot.toastType === "error") return "✕";
                if (toastRoot.toastType === "warning") return "⚠";
                return "ℹ";
            }
            font.pixelSize: 15
            font.bold: true
            color: "#FFFFFF"
            anchors.verticalCenter: parent.verticalCenter
        }

        Text {
            id: msgText
            text: toastRoot.message
            font.pixelSize: 13
            font.weight: Font.Medium
            color: "#FFFFFF"
            elide: Text.ElideRight
            maximumLineCount: 1
            anchors.verticalCenter: parent.verticalCenter
        }
    }

    Connections {
        target: navBridge
        function onToastRequested(msg, type, durationMs) {
            toastRoot.message = msg;
            toastRoot.toastType = type || "info";
            toastRoot.duration = durationMs || 3000;
            toastRoot.y = 24;
            toastRoot.opacity = 1.0;
            hideTimer.restart();
        }
    }
}
