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
        sequence: StandardKey.Copy
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
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacing.md

            Rectangle {
                Layout.fillWidth: true
                height: 38
                radius: Theme.radius.small
                color: themeBridge.color("surface")
                border.color: themeBridge.color("border")

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: Theme.spacing.md
                    anchors.rightMargin: Theme.spacing.md
                    spacing: Theme.spacing.lg

                    RowLayout {
                        spacing: Theme.spacing.xs
                        Text {
                            text: i18nBridge.tr("stat_total_tasks", "Toplam:")
                            font.pixelSize: Theme.typography.sizeSmall
                            color: themeBridge.color("text_secondary")
                        }
                        Text {
                            text: taskViewModel ? taskViewModel.totalTasks.toString() : "0"
                            font.pixelSize: Theme.typography.sizeSmall
                            font.weight: Theme.typography.weightBold
                            color: themeBridge.color("text_primary")
                        }
                    }

                    RowLayout {
                        spacing: Theme.spacing.xs
                        Text {
                            text: i18nBridge.tr("stat_completed_tasks", "Tamamlanan:")
                            font.pixelSize: Theme.typography.sizeSmall
                            color: themeBridge.color("text_secondary")
                        }
                        Text {
                            text: taskViewModel ? taskViewModel.completedTasks.toString() : "0"
                            font.pixelSize: Theme.typography.sizeSmall
                            font.weight: Theme.typography.weightBold
                            color: themeBridge.color("success")
                        }
                    }

                    RowLayout {
                        spacing: Theme.spacing.xs
                        Text {
                            text: i18nBridge.tr("stat_in_progress_tasks", "Devam Eden:")
                            font.pixelSize: Theme.typography.sizeSmall
                            color: themeBridge.color("text_secondary")
                        }
                        Text {
                            text: taskViewModel ? taskViewModel.inProgressTasks.toString() : "0"
                            font.pixelSize: Theme.typography.sizeSmall
                            font.weight: Theme.typography.weightBold
                            color: Theme.accent(themeBridge.currentTheme)
                        }
                    }

                    RowLayout {
                        spacing: Theme.spacing.xs
                        Text {
                            text: i18nBridge.tr("stat_blocked_tasks", "Engellenen:")
                            font.pixelSize: Theme.typography.sizeSmall
                            color: themeBridge.color("text_secondary")
                        }
                        Text {
                            text: taskViewModel ? taskViewModel.blockedTasks.toString() : "0"
                            font.pixelSize: Theme.typography.sizeSmall
                            font.weight: Theme.typography.weightBold
                            color: themeBridge.color("danger")
                        }
                    }
                }
            }
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
                        color: themeBridge.color("text_muted")
                        Layout.preferredWidth: 60
                    }

                    Text {
                        text: i18nBridge.tr("column_task_title", "Görev Adı")
                        font.pixelSize: Theme.typography.sizeSmall
                        font.weight: Theme.typography.weightSemiBold
                        color: themeBridge.color("text_muted")
                        Layout.fillWidth: true
                    }

                    Text {
                        text: i18nBridge.tr("column_priority", "Öncelik")
                        font.pixelSize: Theme.typography.sizeSmall
                        font.weight: Theme.typography.weightSemiBold
                        color: themeBridge.color("text_muted")
                        Layout.preferredWidth: 80
                    }

                    Text {
                        text: i18nBridge.tr("column_status", "Durum")
                        font.pixelSize: Theme.typography.sizeSmall
                        font.weight: Theme.typography.weightSemiBold
                        color: themeBridge.color("text_muted")
                        Layout.preferredWidth: 100
                    }

                    Item { Layout.preferredWidth: 88 }
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: themeBridge.color("border")
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

                    ScrollBar.vertical: AppScrollBar {
                        id: taskScrollBar
                    }

                    delegate: TaskItemDelegate {}

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
                                color: themeBridge.color("text_muted")
                                Layout.alignment: Qt.AlignHCenter
                            }

                            Text {
                                text: i18nBridge.tr("tasks_empty_title", "WBS Ağacı Boş")
                                font.pixelSize: Theme.typography.sizeH3
                                font.weight: Theme.typography.weightSemiBold
                                color: themeBridge.color("text_primary")
                                Layout.alignment: Qt.AlignHCenter
                            }

                            Text {
                                text: i18nBridge.tr("tasks_empty_message", "İlk ana görevi ekleyerek WBS hiyerarşisini oluşturun.")
                                font.pixelSize: Theme.typography.sizeBody
                                color: themeBridge.color("text_secondary")
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
                    color: themeBridge.color("border")
                }

                // Hızlı Görev Ekleme Satırı
                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spacing.md

                    AppTextInput {
                        id: quickAddInput
                        placeholder: i18nBridge.tr("task_quick_add_placeholder", "Seçili görevin altına hızlı görev ekle...")
                        Layout.fillWidth: true
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
