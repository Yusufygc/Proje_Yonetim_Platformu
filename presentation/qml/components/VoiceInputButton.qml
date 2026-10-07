import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"

Rectangle {
    id: voiceBtnRoot

    property var target: null // Hedef TextInput veya TextArea
    signal transcriptReceived(string text)

    // Dikte sonucu tüm düğmelere yayınlanır; yalnızca dinlemeyi başlatan düğme metni alır.
    readonly property string ownerId: "voice-" + Math.random().toString(36).slice(2)
    readonly property bool isActive: voiceBridge && voiceBridge.isListening && voiceBridge.activeOwner === ownerId

    width: 32
    height: 32
    radius: 6
    color: {
        if (voiceBtnRoot.isActive) return Qt.rgba(0.93, 0.27, 0.27, 0.2);
        if (mouseArea.containsMouse) return themeBridge.surfaceRaised;
        return "transparent";
    }
    border.width: 1
    border.color: voiceBtnRoot.isActive ? "#EF4444" : themeBridge.border

    AppIcon {
        name: "mic"
        size: 16
        color: voiceBtnRoot.isActive ? "#EF4444" : themeBridge.textSecondary
        anchors.centerIn: parent
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: voiceBridge.toggleListeningFor(voiceBtnRoot.ownerId)
    }

    Connections {
        target: voiceBridge
        function onTextTranscribed(text) {
            if (voiceBridge.activeOwner !== voiceBtnRoot.ownerId) return;
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
    ToolTip.text: voiceBtnRoot.isActive
        ? i18nBridge.tr("voice_stop_tooltip", "Dinlemeyi durdur")
        : i18nBridge.tr("voice_start_tooltip", "Sesle yaz (Mikrofon)")
    ToolTip.delay: 300
}
