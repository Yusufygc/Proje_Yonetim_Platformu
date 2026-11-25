import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../components"
import "../../theme"

Item {
    id: root

    property int taskId: 0
    property int level: 0
    property int checklistTotal: 0
    property bool isChecklistExpanded: false
    property var checklistItems: []

    visible: checklistTotal > 0 && isChecklistExpanded
    height: visible ? checklistCol.implicitHeight + 8 : 0

    Rectangle {
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.topMargin: 2
        anchors.bottomMargin: 6
        width: 2
        radius: 1
        color: themeBridge.border
    }

    ColumnLayout {
        id: checklistCol
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.leftMargin: 12
        anchors.top: parent.top
        anchors.topMargin: 2
        spacing: 4

        Repeater {
            model: root.checklistItems

            Rectangle {
                id: chkItemRow
                Layout.fillWidth: true
                height: 28
                radius: Theme.radius.small
                color: chkRowHover.hovered ? themeBridge.surfaceAlt : "transparent"

                HoverHandler {
                    id: chkRowHover
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        if (taskViewModel && modelData.id > 0) {
                            taskViewModel.toggleChecklistItem(modelData.id, root.taskId)
                        }
                    }
                }

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 6
                    anchors.rightMargin: 6
                    spacing: Theme.spacing.sm

                    Rectangle {
                        width: 15
                        height: 15
                        radius: 4
                        color: modelData.isDone ? themeBridge.success : "transparent"
                        border.color: modelData.isDone ? themeBridge.success : themeBridge.border
                        border.width: 1.5

                        AppIcon {
                            anchors.centerIn: parent
                            name: "check"
                            size: 10
                            color: "#FFFFFF"
                            visible: modelData.isDone === true
                        }
                    }

                    Text {
                        id: chkItemLabel
                        text: modelData.text || ""
                        font.pixelSize: Theme.typography.sizeSmall
                        font.strikeout: modelData.isDone === true
                        color: modelData.isDone ? themeBridge.textMuted : themeBridge.textPrimary
                        Layout.fillWidth: true
                        elide: Text.ElideRight

                        ToolTip.visible: chkRowHover.hovered && chkItemLabel.truncated
                        ToolTip.text: modelData.text || ""
                        ToolTip.delay: 400
                    }

                    AppButton {
                        iconName: "x"
                        btnVariant: "secondary"
                        implicitWidth: 22
                        implicitHeight: 22
                        opacity: chkRowHover.hovered ? 1 : 0
                        visible: opacity > 0
                        onClicked: {
                            if (taskViewModel && modelData.id > 0) {
                                taskViewModel.deleteChecklistItem(modelData.id, root.taskId)
                            }
                        }
                    }
                }
            }
        }
    }
}
