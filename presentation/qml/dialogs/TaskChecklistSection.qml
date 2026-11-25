import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"
import "../theme"

ColumnLayout {
    id: root

    property var checklistItems: []
    readonly property bool hasInputFocus: newChecklistInput.hasTextFocus
    signal submitRequested()

    function clearInput() {
        newChecklistInput.text = ""
    }

    function addChecklistItem() {
        var txt = newChecklistInput.text.trim()
        if (txt.length > 0) {
            var arr = root.checklistItems.slice()
            arr.push({ "id": 0, "text": txt, "isDone": false })
            root.checklistItems = arr
            newChecklistInput.text = ""
        }
    }

    spacing: Theme.spacing.sm

    Text {
        text: i18nBridge.tr("label_checklist", "Kontrol Listesi (Checklist)")
        font.pixelSize: Theme.typography.sizeSmall
        font.weight: Theme.typography.weightMedium
        color: themeBridge.textSecondary
        Layout.topMargin: Theme.spacing.xs
    }

    RowLayout {
        Layout.fillWidth: true
        spacing: Theme.spacing.sm

        AppTextInput {
            id: newChecklistInput
            placeholder: i18nBridge.tr("task_checklist_placeholder", "Yeni kontrol maddesi ekle...")
            Layout.fillWidth: true
            onAccepted: {
                if (newChecklistInput.text.trim().length > 0) root.addChecklistItem()
                else root.submitRequested()
            }
        }

        AppButton {
            text: i18nBridge.tr("action_add", "Ekle")
            btnVariant: "secondary"
            Layout.preferredHeight: 38
            Layout.alignment: Qt.AlignVCenter
            onClicked: root.addChecklistItem()
        }
    }

    ColumnLayout {
        Layout.fillWidth: true
        spacing: Theme.spacing.xs

        Repeater {
            model: root.checklistItems

            Rectangle {
                Layout.fillWidth: true
                height: 32
                radius: Theme.radius.small
                color: themeBridge.surfaceAlt

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: Theme.spacing.sm
                    anchors.rightMargin: Theme.spacing.sm
                    spacing: Theme.spacing.sm

                    Rectangle {
                        width: 16
                        height: 16
                        radius: 4
                        color: modelData.isDone ? themeBridge.success : "transparent"
                        border.color: modelData.isDone ? themeBridge.success : themeBridge.border
                        border.width: 1.5

                        AppIcon {
                            anchors.centerIn: parent
                            name: "check"
                            size: 11
                            color: "#FFFFFF"
                            visible: modelData.isDone === true
                        }

                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                var arr = root.checklistItems.slice()
                                arr[index] = {
                                    "id": modelData.id || 0,
                                    "text": modelData.text || "",
                                    "isDone": !(modelData.isDone === true)
                                }
                                root.checklistItems = arr
                            }
                        }
                    }

                    Text {
                        id: chkItemText
                        text: modelData.text || ""
                        font.pixelSize: Theme.typography.sizeSmall
                        font.strikeout: modelData.isDone === true
                        color: modelData.isDone ? themeBridge.textMuted : themeBridge.textPrimary
                        Layout.fillWidth: true
                        elide: Text.ElideRight

                        ToolTip.visible: chkHoverArea.containsMouse && chkItemText.truncated
                        ToolTip.text: modelData.text || ""
                        ToolTip.delay: 400

                        MouseArea {
                            id: chkHoverArea
                            anchors.fill: parent
                            hoverEnabled: true
                            acceptedButtons: Qt.NoButton
                        }
                    }

                    AppButton {
                        iconName: "x"
                        btnVariant: "secondary"
                        implicitWidth: 24
                        implicitHeight: 24
                        onClicked: {
                            var arr = root.checklistItems.slice()
                            arr.splice(index, 1)
                            root.checklistItems = arr
                        }
                    }
                }
            }
        }
    }
}
