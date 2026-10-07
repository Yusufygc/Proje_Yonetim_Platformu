import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../components"
import "../../theme"

Rectangle {
    id: root

    width: ListView.view ? (ListView.view.width - 14) : 400
    height: 48
    radius: Theme.radius.small

    property bool isSelected: taskViewModel ? taskViewModel.selectedTaskId === model.taskId : false
    // MouseArea.containsMouse çocuk butonların üstünde false olur; HoverHandler pasif olduğu için satırın tamamını izler
    property bool isHovered: rowHoverHandler.hovered

    color: {
        if (isSelected) return Theme.accentAlpha(themeBridge.currentTheme, 0.15)
        if (isHovered) return themeBridge.color("hover_overlay")
        return "transparent"
    }

    border.color: isSelected ? Theme.accent(themeBridge.currentTheme) : "transparent"
    border.width: 1

    Behavior on color { ColorAnimation { duration: Theme.animation.fast } }

    HoverHandler {
        id: rowHoverHandler
    }

    MouseArea {
        id: hoverArea
        anchors.fill: parent
        acceptedButtons: Qt.LeftButton | Qt.RightButton
        onClicked: function(mouse) {
            if (taskViewModel) {
                taskViewModel.selectTask(model.taskId)
                if (mouse.button === Qt.RightButton) {
                    contextMenu.popup()
                }
            }
        }
        onDoubleClicked: {
            if (taskViewModel) {
                taskViewModel.openEditDialog(model.taskId)
            }
        }
    }

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 8 + (model.level * 22)
        anchors.rightMargin: 12
        spacing: Theme.spacing.sm

        // Aç / Kapa Oku
        Item {
            width: 20
            height: 20
            visible: model.hasChildren

            Text {
                anchors.centerIn: parent
                text: model.isExpanded ? "▼" : "▶"
                font.pixelSize: 10
                color: themeBridge.color("text_secondary")
            }

            MouseArea {
                anchors.fill: parent
                onClicked: {
                    if (taskViewModel) {
                        taskViewModel.taskModel.toggleExpanded(model.taskId)
                    }
                }
            }
        }

        Item {
            width: 20
            height: 20
            visible: !model.hasChildren
        }

        // Durum Checkbox'ı
        Rectangle {
            width: 18
            height: 18
            radius: 4
            color: model.status === "DONE" ? themeBridge.color("success") : "transparent"
            border.color: model.status === "DONE" ? themeBridge.color("success") : themeBridge.color("border")
            border.width: 1.5

            AppIcon {
                anchors.centerIn: parent
                name: "check"
                size: 12
                color: "#FFFFFF"
                visible: model.status === "DONE"
            }

            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                onClicked: {
                    if (taskViewModel) {
                        taskViewModel.selectTask(model.taskId)
                        taskViewModel.toggleTaskStatus(model.taskId)
                    }
                }
            }
        }

        // WBS Kodu
        Text {
            text: model.wbsCode
            font.pixelSize: Theme.typography.sizeSmall
            font.weight: Theme.typography.weightBold
            font.family: "monospace"
            color: Theme.accent(themeBridge.currentTheme)
        }

        // Görev Başlığı
        Text {
            id: titleTextItem
            text: model.title
            font.pixelSize: Theme.typography.sizeBody
            font.strikeout: model.status === "DONE"
            color: model.status === "DONE" ? themeBridge.color("text_muted") : themeBridge.color("text_primary")
            Layout.fillWidth: true
            elide: Text.ElideRight

            ToolTip.visible: titleHoverArea.containsMouse && titleTextItem.truncated
            ToolTip.text: model.title
            ToolTip.delay: 400

            MouseArea {
                id: titleHoverArea
                anchors.fill: parent
                hoverEnabled: true
                acceptedButtons: Qt.NoButton
            }
        }

        // Checklist İlerleme Rozeti
        Rectangle {
            visible: model.checklistTotal > 0
            implicitWidth: chkLayout.implicitWidth + 10
            implicitHeight: 20
            radius: 10
            color: themeBridge.color("surface_alt")
            border.color: themeBridge.color("border")

            RowLayout {
                id: chkLayout
                anchors.centerIn: parent
                spacing: 3

                AppIcon {
                    name: "check"
                    size: 10
                    color: model.checklistDone === model.checklistTotal ? themeBridge.color("success") : themeBridge.color("text_secondary")
                }

                Text {
                    text: model.checklistDone + "/" + model.checklistTotal
                    font.pixelSize: 10
                    font.weight: Theme.typography.weightMedium
                    color: themeBridge.color("text_secondary")
                }
            }
        }

        // Görev Tipi Rozeti
        AppBadge {
            text: {
                switch (model.taskType) {
                    case "GROUP": return i18nBridge.tr("task_type_group", "Grup");
                    case "BUG": return i18nBridge.tr("task_type_bug", "Hata");
                    case "IMPROVEMENT": return i18nBridge.tr("task_type_improvement", "İyileştirme");
                    case "RESEARCH": return i18nBridge.tr("task_type_research", "Araştırma");
                    case "DOCUMENTATION": return i18nBridge.tr("task_type_documentation", "Dokümantasyon");
                    case "DESIGN": return i18nBridge.tr("task_type_design", "Tasarım");
                    case "TEST": return i18nBridge.tr("task_type_test", "Test");
                    case "REVIEW": return i18nBridge.tr("task_type_review", "İnceleme");
                    default: return model.taskType;
                }
            }
            variant: "neutral"
            size: "sm"
            visible: model.taskType !== "TASK"
        }

        // Öncelik Rozeti
        AppBadge {
            text: {
                if (model.priority === "CRITICAL") return i18nBridge.tr("priority_critical", "Kritik")
                if (model.priority === "HIGH") return i18nBridge.tr("priority_high", "Yüksek")
                if (model.priority === "LOW") return i18nBridge.tr("priority_low", "Düşük")
                return i18nBridge.tr("priority_medium", "Orta")
            }
            variant: {
                if (model.priority === "CRITICAL") return "danger"
                if (model.priority === "HIGH") return "warning"
                if (model.priority === "LOW") return "neutral"
                return "info"
            }
            size: "sm"
        }

        // Durum Rozeti
        StatusIndicator {
            status: model.status
        }

        // Hızlı Butonlar (Hover sırasında görünür)
        RowLayout {
            spacing: 2
            opacity: isHovered || isSelected ? 1 : 0
            Behavior on opacity { NumberAnimation { duration: Theme.animation.fast } }

            AppButton {
                iconName: "plus"
                btnVariant: "secondary"
                implicitWidth: 26
                implicitHeight: 26
                onClicked: {
                    if (taskViewModel) {
                        taskViewModel.openCreateDialog(model.taskId)
                    }
                }
            }

            AppButton {
                iconName: "copy"
                btnVariant: "secondary"
                implicitWidth: 26
                implicitHeight: 26
                onClicked: {
                    if (taskViewModel) {
                        taskViewModel.copyTaskToClipboard(model.taskId)
                    }
                }
            }

            AppButton {
                iconName: "pencil"
                btnVariant: "secondary"
                implicitWidth: 26
                implicitHeight: 26
                onClicked: {
                    if (taskViewModel) {
                        taskViewModel.openEditDialog(model.taskId)
                    }
                }
            }
        }
    }

    // Sağ Tık Menüsü
    Menu {
        id: contextMenu

        MenuItem {
            text: i18nBridge.tr("task_add_child", "Alt Görev Ekle")
            onTriggered: {
                if (taskViewModel) taskViewModel.openCreateDialog(model.taskId)
            }
        }

        MenuItem {
            text: i18nBridge.tr("action_edit", "Düzenle")
            onTriggered: {
                if (taskViewModel) taskViewModel.openEditDialog(model.taskId)
            }
        }

        MenuSeparator {}

        MenuItem {
            text: i18nBridge.tr("action_copy_task", "Panoya Kopyala")
            onTriggered: {
                if (taskViewModel) taskViewModel.copyTaskToClipboard(model.taskId)
            }
        }

        MenuItem {
            text: i18nBridge.tr("action_duplicate_task", "Görevi Çoğalt")
            onTriggered: {
                if (taskViewModel) taskViewModel.duplicateTask(model.taskId)
            }
        }

        MenuSeparator {}

        MenuItem {
            text: i18nBridge.tr("action_delete", "Sil")
            onTriggered: {
                if (taskViewModel) taskViewModel.deleteTask(model.taskId)
            }
        }
    }
}
