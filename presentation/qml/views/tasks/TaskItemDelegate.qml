import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../components"
import "../../theme"

Rectangle {
    id: root

    readonly property var ownerList: ListView.view
    readonly property int itemTaskId: model.taskId
    readonly property int topRowHeight: 48

    width: ownerList ? (ownerList.width - 14) : 400
    height: topRowHeight + (checklistPanel.visible ? checklistPanel.height + 6 : 0)
    radius: Theme.radius.small

    property bool isSelected: taskViewModel ? taskViewModel.selectedTaskId === model.taskId : false
    // MouseArea.containsMouse çocuk butonların üstünde false olur; HoverHandler pasif olduğu için satırın tamamını izler
    property bool isHovered: rowHoverHandler.hovered
    property bool isDraggedItem: ownerList ? ownerList.draggedTaskId === model.taskId : false
    property bool isDropBefore: ownerList ? (ownerList.dropTargetTaskId === model.taskId && ownerList.dropPosition === "before" && !isDraggedItem) : false
    property bool isDropAfter: ownerList ? (ownerList.dropTargetTaskId === model.taskId && ownerList.dropPosition === "after" && !isDraggedItem) : false
    property bool isDropInto: ownerList ? (ownerList.dropTargetTaskId === model.taskId && ownerList.dropPosition === "into" && !isDraggedItem) : false

    opacity: isDraggedItem ? 0.45 : 1.0

    color: {
        if (isDropInto) return Theme.accentAlpha(themeBridge.currentTheme, 0.22)
        if (isSelected) return Theme.accentAlpha(themeBridge.currentTheme, 0.15)
        if (isHovered) return themeBridge.hoverOverlay
        return "transparent"
    }

    border.color: (isDropInto || isSelected) ? Theme.accent(themeBridge.currentTheme) : "transparent"
    border.width: isDropInto ? 2 : 1

    Behavior on color { ColorAnimation { duration: Theme.animation.fast } }

    HoverHandler {
        id: rowHoverHandler
    }

    // Üst/Alt Sürükle-Bırak Hedef Çizgileri
    Rectangle {
        visible: root.isDropBefore
        z: 20
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 2
        color: Theme.accent(themeBridge.currentTheme)

        Rectangle {
            width: 6
            height: 6
            radius: 3
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            color: Theme.accent(themeBridge.currentTheme)
        }
    }

    Rectangle {
        visible: root.isDropAfter
        z: 20
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        height: 2
        color: Theme.accent(themeBridge.currentTheme)

        Rectangle {
            width: 6
            height: 6
            radius: 3
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            color: Theme.accent(themeBridge.currentTheme)
        }
    }

    Item {
        id: topRow
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: root.topRowHeight

        MouseArea {
            id: hoverArea
            anchors.fill: parent
            acceptedButtons: Qt.LeftButton | Qt.RightButton
            preventStealing: true
            property real pressSceneX: 0
            property real pressSceneY: 0
            property bool dragStarted: false
            property bool isDragging: false
            property bool suppressNextClick: false
            cursorShape: dragStarted ? Qt.ClosedHandCursor : Qt.ArrowCursor

            onPressed: function(mouse) {
                if (mouse.button === Qt.LeftButton && root.ownerList) {
                    var p = hoverArea.mapToItem(root.ownerList, mouse.x, mouse.y)
                    pressSceneX = p.x
                    pressSceneY = p.y
                    dragStarted = false
                    isDragging = true
                }
            }
            onPositionChanged: function(mouse) {
                if (!(mouse.buttons & Qt.LeftButton) || !isDragging || !root.ownerList) return
                var p = hoverArea.mapToItem(root.ownerList, mouse.x, mouse.y)
                if (!dragStarted) {
                    var dx = p.x - pressSceneX
                    var dy = p.y - pressSceneY
                    if (dx * dx + dy * dy >= 36) {
                        dragStarted = true
                        root.ownerList.beginDrag(model.taskId, model.title, p.x, p.y)
                    }
                }
                if (dragStarted) {
                    root.ownerList.updateDrag(p.x, p.y)
                }
            }
            onReleased: function(mouse) {
                var dropped = dragStarted
                dragStarted = false
                isDragging = false
                suppressNextClick = dropped
                if (dropped && root.ownerList) {
                    root.ownerList.finishDrag()
                }
            }
            onCanceled: {
                if (dragStarted && root.ownerList) {
                    root.ownerList.cancelDrag()
                }
                dragStarted = false
                isDragging = false
                suppressNextClick = false
            }
            onClicked: function(mouse) {
                if (suppressNextClick) {
                    suppressNextClick = false
                    return
                }
                if (taskViewModel) {
                    taskViewModel.selectTask(model.taskId)
                    if (mouse.button === Qt.LeftButton && model.checklistTotal > 0) {
                        taskViewModel.taskModel.toggleChecklistExpanded(model.taskId)
                    } else if (mouse.button === Qt.RightButton) {
                        contextMenu.popup()
                    }
                }
            }
            onDoubleClicked: function(mouse) {
                if (mouse.button === Qt.LeftButton && taskViewModel) {
                    taskDialogViewModel.openEditDialog(model.taskId)
                }
            }
        }

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 6 + (model.level * 22)
            anchors.rightMargin: 12
            spacing: Theme.spacing.sm

            // Sürükle-Bırak Tutamacı (Grip)
            Grid {
                columns: 2
                rowSpacing: 2
                columnSpacing: 2
                opacity: (isHovered || isSelected) ? 0.85 : 0.35
                Behavior on opacity { NumberAnimation { duration: Theme.animation.fast } }
                Repeater {
                    model: 6
                    Rectangle {
                        width: 2.5
                        height: 2.5
                        radius: 1.25
                        color: themeBridge.textSecondary
                    }
                }
            }

            // Aç / Kapa Oku
            Item {
                width: 20
                height: 20
                visible: model.hasChildren

                AppIcon {
                    anchors.centerIn: parent
                    name: model.isExpanded ? "chevron-down" : "chevron-right"
                    size: 13
                    color: themeBridge.textSecondary
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
                color: model.status === "DONE" ? themeBridge.success : "transparent"
                border.color: model.status === "DONE" ? themeBridge.success : themeBridge.border
                border.width: 1.5

                AppIcon {
                    anchors.centerIn: parent
                    name: "check"
                    size: 12
                    color: "#FFFFFF"
                    visible: model.status === "DONE"
                }

                // Üst görevi de bu kutu kapatır; alt görevler bitse bile üst görev kendiliğinden kapanmaz.
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
                color: model.status === "DONE" ? themeBridge.textMuted : themeBridge.textPrimary
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

            // Checklist İlerleme Rozeti (Tıklanınca alt maddeleri açar/kapatır)
            TaskChecklistBadge {
                taskId: model.taskId
                checklistTotal: model.checklistTotal
                checklistDone: model.checklistDone
                isChecklistExpanded: model.isChecklistExpanded
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
                            taskDialogViewModel.openCreateDialog(model.taskId)
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
                            taskDialogViewModel.openEditDialog(model.taskId)
                        }
                    }
                }
            }
        }
    }

    // Açılır Checklist Alt Paneli
    TaskChecklistPanel {
        id: checklistPanel
        taskId: model.taskId
        level: model.level
        checklistTotal: model.checklistTotal
        isChecklistExpanded: model.isChecklistExpanded
        checklistItems: model.checklistItems
        anchors.top: topRow.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.leftMargin: 42 + (model.level * 22)
        anchors.rightMargin: 16
    }

    // Sağ Tık Menüsü
    TaskContextMenu {
        id: contextMenu
        taskId: model.taskId
    }
}
