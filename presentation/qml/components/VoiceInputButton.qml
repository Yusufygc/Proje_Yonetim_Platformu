import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"

Rectangle {
    id: voiceBtnRoot

    property var target: null // Hedef TextInput veya TextArea
    signal transcriptReceived(string text)

    width: 32
    height: 32
    radius: 6
    color: {
        if (voiceBridge.isListening) return Qt.rgba(0.93, 0.27, 0.27, 0.2);
        if (mouseArea.containsMouse) return themeBridge.surfaceHover;
        return "transparent";
    }
    border.width: 1
    border.color: voiceBridge.isListening ? "#EF4444" : themeBridge.border

    AppIcon {
        name: "mic"
        size: 16
        color: voiceBridge.isListening ? "#EF4444" : themeBridge.textSecondary
        anchors.centerIn: parent
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: voiceBridge.toggleListening()
    }

    Connections {
        target: voiceBridge
        function onTextTranscribed(text) {
            voiceBtnRoot.transcriptReceived(text);
            if (voiceBtnRoot.target) {
                var current = voiceBtnRoot.target.text || "";
                if (current.length > 0 && !current.endsWith(" ")) {
                    voiceBtnRoot.target.text = current + " " + text;
                } else {
                    voiceBtnRoot.target.text = current + text;
                }
            }
        }
    }

    ToolTip.visible: mouseArea.containsMouse
    ToolTip.text: voiceBridge.isListening
        ? i18nBridge.tr("voice_stop_tooltip", "Dinlemeyi durdur")
        : i18nBridge.tr("voice_start_tooltip", "Sesle yaz (Mikrofon)")
    ToolTip.delay: 300
}
