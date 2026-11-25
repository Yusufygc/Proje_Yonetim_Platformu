import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../components"
import "../../theme"

Rectangle {
    id: root

    property int taskId: 0
    property int checklistTotal: 0
    property int checklistDone: 0
    property bool isChecklistExpanded: false

    visible: checklistTotal > 0
    implicitWidth: chkLayout.implicitWidth + 12
    implicitHeight: 22
    radius: 11
    color: isChecklistExpanded
           ? Theme.accentAlpha(themeBridge.currentTheme, 0.14)
           : themeBridge.surfaceAlt
    border.color: isChecklistExpanded
                  ? Theme.accent(themeBridge.currentTheme)
                  : themeBridge.border
    border.width: 1

    RowLayout {
        id: chkLayout
        anchors.centerIn: parent
        spacing: 4

        AppIcon {
            name: "check"
            size: 11
            color: root.checklistDone === root.checklistTotal
                   ? themeBridge.success
                   : (root.isChecklistExpanded ? Theme.accent(themeBridge.currentTheme) : themeBridge.textSecondary)
        }

        Text {
            text: root.checklistDone + "/" + root.checklistTotal
            font.pixelSize: 10
            font.weight: Theme.typography.weightMedium
            color: root.isChecklistExpanded
                   ? Theme.accent(themeBridge.currentTheme)
                   : themeBridge.textSecondary
        }

        AppIcon {
            name: root.isChecklistExpanded ? "chevron-down" : "chevron-right"
            size: 10
            color: root.isChecklistExpanded
                   ? Theme.accent(themeBridge.currentTheme)
                   : themeBridge.textMuted
        }
    }

    ToolTip.visible: chkBadgeMouse.containsMouse
    ToolTip.text: i18nBridge.tr("task_checklist_toggle_tip", "Checklist maddelerini aç/kapat")
    ToolTip.delay: 400

    MouseArea {
        id: chkBadgeMouse
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: {
            if (taskViewModel) {
                taskViewModel.selectTask(root.taskId)
                taskViewModel.taskModel.toggleChecklistExpanded(root.taskId)
            }
        }
    }
}
