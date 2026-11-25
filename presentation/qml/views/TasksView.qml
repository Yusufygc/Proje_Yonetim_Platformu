import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"
import "../dialogs"
import "../theme"
import "tasks"

Item {
    id: tasksViewRoot
    anchors.fill: parent

    Shortcut {
        sequences: [StandardKey.Copy]
        enabled: tasksViewRoot.visible && taskViewModel && taskViewModel.selectedTaskId > 0
        onActivated: {
            taskViewModel.copyTaskToClipboard(taskViewModel.selectedTaskId)
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacing.xl
        spacing: Theme.spacing.lg

        // Üst Araç Çubuğu
        TaskToolbar {
            Layout.fillWidth: true
        }

        // Görev İstatistikleri Rozet Çubuğu
        TaskStatsBar {
            Layout.fillWidth: true
        }

        // Ana Görev Ağacı (WBS)
        AppCard {
            id: taskTreeCard
            Layout.fillWidth: true
            Layout.fillHeight: true

            property real savedScrollY: 0

            Connections {
                target: taskViewModel ? taskViewModel.taskModel : null

                function onModelAboutToBeReset() {
                    taskListView.cancelDrag()
                    if (taskListView.contentY > 0) {
                        taskTreeCard.savedScrollY = taskListView.contentY
                    } else {
                        taskTreeCard.savedScrollY = 0
                    }
                }

                function onModelReset() {
                    if (taskTreeCard.savedScrollY > 0) {
                        var maxY = Math.max(0, taskListView.contentHeight - taskListView.height)
                        taskListView.contentY = Math.min(taskTreeCard.savedScrollY, maxY)
                        Qt.callLater(function() {
                            if (taskListView && taskListView.contentHeight > 0) {
                                var limitY = Math.max(0, taskListView.contentHeight - taskListView.height)
                                taskListView.contentY = Math.min(taskTreeCard.savedScrollY, limitY)
                            }
                        })
                    }
                }
            }

            Connections {
                target: taskViewModel

                function onSelectedProjectChanged(projectId) {
                    taskTreeCard.savedScrollY = 0
                    if (taskListView) {
                        taskListView.contentY = 0
                    }
                }
            }

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: Theme.spacing.md
                spacing: Theme.spacing.sm

                // Liste Başlığı / Kolon Başlıkları
                RowLayout {
                    Layout.fillWidth: true
                    Layout.leftMargin: Theme.spacing.sm
                    Layout.rightMargin: Theme.spacing.sm
                    height: 28

                    Text {
                        text: i18nBridge.tr("column_wbs_code", "Kod")
                        font.pixelSize: Theme.typography.sizeSmall
                        font.weight: Theme.typography.weightSemiBold
                        color: themeBridge.textMuted
                        Layout.preferredWidth: 60
                    }

                    Text {
                        text: i18nBridge.tr("column_task_title", "Görev Adı")
                        font.pixelSize: Theme.typography.sizeSmall
                        font.weight: Theme.typography.weightSemiBold
                        color: themeBridge.textMuted
                        Layout.fillWidth: true
                    }

                    Text {
                        text: i18nBridge.tr("column_priority", "Öncelik")
                        font.pixelSize: Theme.typography.sizeSmall
                        font.weight: Theme.typography.weightSemiBold
                        color: themeBridge.textMuted
                        Layout.preferredWidth: 80
                    }

                    Text {
                        text: i18nBridge.tr("column_status", "Durum")
                        font.pixelSize: Theme.typography.sizeSmall
                        font.weight: Theme.typography.weightSemiBold
                        color: themeBridge.textMuted
                        Layout.preferredWidth: 100
                    }

                    Item { Layout.preferredWidth: 88 }
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: themeBridge.border
                }

                // WBS Görev Listesi
                ListView {
                    id: taskListView
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    model: taskViewModel ? taskViewModel.taskModel : null
                    spacing: 2
                    boundsBehavior: Flickable.StopAtBounds

                    property int draggedTaskId: 0
                    property string draggedTaskTitle: ""
                    property int dropTargetTaskId: 0
                    property string dropPosition: "" // "before" | "after" | "into"
                    property real ghostX: 0
                    property real ghostY: 0

                    function beginDrag(taskId, taskTitle, px, py) {
                        draggedTaskId = taskId
                        draggedTaskTitle = taskTitle
                        updateDrag(px, py)
                    }

                    function updateDrag(px, py) {
                        ghostX = px
                        ghostY = py
                        var clampedX = Math.max(12, Math.min(width - 24, px))
                        var contentPos = mapToItem(contentItem, clampedX, py)
                        var idx = indexAt(contentPos.x, contentPos.y)
                        if (idx < 0) {
                            dropTargetTaskId = 0
                            dropPosition = ""
                            return
                        }
                        var targetItem = itemAtIndex(idx)
                        if (!targetItem || targetItem.itemTaskId === draggedTaskId) {
                            dropTargetTaskId = 0
                            dropPosition = ""
                            return
                        }
                        var localPos = mapToItem(targetItem, px, py)
                        dropTargetTaskId = targetItem.itemTaskId
                        if (localPos.y < 14) {
                            dropPosition = "before"
                        } else if (localPos.y > 34) {
                            dropPosition = "after"
                        } else {
                            dropPosition = "into"
                        }
                    }

                    function finishDrag() {
                        var srcId = draggedTaskId
                        var dstId = dropTargetTaskId
                        var pos = dropPosition
                        cancelDrag()
                        if (taskViewModel && srcId > 0 && dstId > 0 && srcId !== dstId && pos !== "") {
                            taskViewModel.moveTaskRelative(srcId, dstId, pos)
                        }
                    }

                    function cancelDrag() {
                        draggedTaskId = 0
                        draggedTaskTitle = ""
                        dropTargetTaskId = 0
                        dropPosition = ""
                    }

                    Timer {
                        id: dragAutoScrollTimer
                        interval: 35
                        repeat: true
                        running: taskListView.draggedTaskId > 0 && (taskListView.ghostY < 28 || taskListView.ghostY > taskListView.height - 28)
                        onTriggered: {
                            var step = taskListView.ghostY < 28 ? -10 : 10
                            var maxY = Math.max(0, taskListView.contentHeight - taskListView.height)
                            taskListView.contentY = Math.max(0, Math.min(maxY, taskListView.contentY + step))
                            taskListView.updateDrag(taskListView.ghostX, taskListView.ghostY)
                        }
                    }

                    ScrollBar.vertical: AppScrollBar {
                        id: taskScrollBar
                    }

                    delegate: TaskItemDelegate {}

                    // Sürükleme Hayalet Kartı (Drag Ghost)
                    Rectangle {
                        id: dragGhost
                        visible: taskListView.draggedTaskId > 0
                        z: 100
                        x: Math.max(4, Math.min(taskListView.width - width - 20, taskListView.ghostX - 24))
                        y: Math.max(0, Math.min(taskListView.height - height, taskListView.ghostY - height / 2))
                        width: Math.min(340, Math.max(180, taskListView.width - 40))
                        height: 36
                        radius: Theme.radius.small
                        color: themeBridge.surface
                        border.color: Theme.accent(themeBridge.currentTheme)
                        border.width: 1.5
                        opacity: 0.92

                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 10
                            anchors.rightMargin: 10
                            spacing: 8

                            AppIcon {
                                name: "tasks"
                                size: 14
                                color: Theme.accent(themeBridge.currentTheme)
                            }

                            Text {
                                text: taskListView.draggedTaskTitle
                                font.pixelSize: Theme.typography.sizeSmall
                                font.weight: Theme.typography.weightMedium
                                color: themeBridge.textPrimary
                                Layout.fillWidth: true
                                elide: Text.ElideRight
                            }
                        }
                    }

                    // Boş Durum
                    Item {
                        anchors.centerIn: parent
                        width: 320
                        height: 200
                        visible: taskListView.count === 0

                        ColumnLayout {
                            anchors.centerIn: parent
                            spacing: Theme.spacing.md

                            AppIcon {
                                name: "tasks"
                                size: 48
                                color: themeBridge.textMuted
                                Layout.alignment: Qt.AlignHCenter
                            }

                            Text {
                                text: i18nBridge.tr("tasks_empty_title", "WBS Ağacı Boş")
                                font.pixelSize: Theme.typography.sizeH3
                                font.weight: Theme.typography.weightSemiBold
                                color: themeBridge.textPrimary
                                Layout.alignment: Qt.AlignHCenter
                            }

                            Text {
                                text: i18nBridge.tr("tasks_empty_message", "İlk ana görevi ekleyerek WBS hiyerarşisini oluşturun.")
                                font.pixelSize: Theme.typography.sizeBody
                                color: themeBridge.textSecondary
                                Layout.alignment: Qt.AlignHCenter
                            }

                            AppButton {
                                text: i18nBridge.tr("task_add_root_plain", "Ana Görev Ekle")
                                iconName: "plus"
                                btnVariant: "primary"
                                Layout.alignment: Qt.AlignHCenter
                                onClicked: {
                                    if (taskViewModel) taskDialogViewModel.openCreateDialog(0)
                                }
                            }
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: themeBridge.border
                }

                // Hızlı Görev Ekleme Satırı
                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spacing.md

                    AppTextInput {
                        id: quickAddInput
                        placeholder: i18nBridge.tr("task_quick_add_placeholder", "Seçili görevin altına hızlı görev ekle...")
                        Layout.fillWidth: true
                        showVoiceInput: true
                        onAccepted: {
                            if (taskViewModel && text.trim().length > 0) {
                                taskViewModel.quickAddTask(text.trim())
                                text = ""
                            }
                        }
                    }

                    AppButton {
                        text: i18nBridge.tr("task_quick_add_button", "Hızlı Ekle")
                        iconName: "plus"
                        btnVariant: "secondary"
                        onClicked: {
                            if (taskViewModel && quickAddInput.text.trim().length > 0) {
                                taskViewModel.quickAddTask(quickAddInput.text.trim())
                                quickAddInput.text = ""
                            }
                        }
                    }
                }
            }
        }
    }

    // Modal Görev Dialogu
    TaskDialog {
        id: taskDialog
    }
}
