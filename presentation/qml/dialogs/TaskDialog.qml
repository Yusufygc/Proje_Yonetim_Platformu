import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"
import "../theme"

Rectangle {
    id: root

    visible: taskViewModel ? taskViewModel.isDialogOpen : false
    anchors.fill: parent
    color: "#80000000"
    z: 999

    MouseArea {
        anchors.fill: parent
        onClicked: { /* modal arka plan tıklaması diyalog dışını engeller */ }
    }

    Shortcut {
        sequence: "Escape"
        enabled: root.visible
        onActivated: taskViewModel.closeDialog()
    }

    property var checklistItems: []

    Connections {
        target: taskViewModel
        function onDialogStateChanged() {
            if (taskViewModel && taskViewModel.isDialogOpen) {
                var init = taskViewModel.dialogInitialData
                titleInput.text = init.title || ""
                descInput.text = init.description || ""
                statusCombo.selectedValue = init.status || "TODO"
                priorityCombo.selectedValue = init.priority || "MEDIUM"
                typeCombo.selectedValue = init.task_type || "TASK"
                newChecklistInput.text = ""

                var chk = []
                if (init.checklist && Array.isArray(init.checklist)) {
                    for (var i = 0; i < init.checklist.length; i++) {
                        chk.push(init.checklist[i].text)
                    }
                }
                root.checklistItems = chk
            }
        }
    }

    AppCard {
        id: dialogCard
        width: Math.min(parent.width - 48, 620)
        height: Math.min(parent.height - 48, 680)
        anchors.centerIn: parent

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: Theme.spacing.xl
            spacing: Theme.spacing.md

            // Başlık Çubuğu
            RowLayout {
                Layout.fillWidth: true
                spacing: Theme.spacing.sm

                AppIcon {
                    name: "tasks"
                    size: 22
                    color: Theme.accent(themeBridge.currentTheme)
                }

                Text {
                    text: {
                        if (!taskViewModel) return ""
                        if (taskViewModel.dialogMode === "edit") return i18nBridge.tr("task_dialog_edit_title", "Görevi Düzenle")
                        if (taskViewModel.dialogMode === "create_subtask") return i18nBridge.tr("task_add_child", "Alt Görev Ekle")
                        return i18nBridge.tr("task_dialog_new_title", "Yeni Görev Ekle")
                    }
                    font.pixelSize: Theme.typography.sizeH3
                    font.weight: Theme.typography.weightBold
                    color: themeBridge.color("text_primary")
                    Layout.fillWidth: true
                }

                AppButton {
                    iconName: "x"
                    btnVariant: "secondary"
                    implicitWidth: 32
                    implicitHeight: 32
                    onClicked: taskViewModel.closeDialog()
                }
            }

            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: themeBridge.color("border")
            }

            // Form Kaydırılabilir Alan
            ScrollView {
                id: formScroll
                Layout.fillWidth: true
                Layout.fillHeight: true
                contentWidth: availableWidth
                clip: true

                ScrollBar.vertical: AppScrollBar { }

                ColumnLayout {
                    width: formScroll.availableWidth - 16
                    spacing: Theme.spacing.md

                    // Görev Başlığı
                    AppTextInput {
                        id: titleInput
                        label: i18nBridge.tr("task_dialog_title_label", "Görev Başlığı *")
                        placeholder: i18nBridge.tr("task_dialog_title_placeholder", "Görevin adını girin...")
                        Layout.fillWidth: true
                        showVoiceInput: true
                    }

                    // Açıklama
                    AppTextInput {
                        id: descInput
                        label: i18nBridge.tr("label_description", "Açıklama")
                        placeholder: i18nBridge.tr("task_dialog_desc_placeholder", "Görevi açıklayın (isteğe bağlı)...")
                        isTextArea: true
                        Layout.fillWidth: true
                        showVoiceInput: true
                    }

                    // Seçimler Satırı (Durum, Öncelik, Tip)
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: Theme.spacing.md

                        AppComboBox {
                            id: statusCombo
                            label: i18nBridge.tr("label_status", "Durum")
                            Layout.fillWidth: true
                            Layout.preferredWidth: 1
                            model: [
                                { "text": i18nBridge.tr("task_status_todo", "Yapılacak"), "value": "TODO" },
                                { "text": i18nBridge.tr("task_status_in_progress", "Devam Ediyor"), "value": "IN_PROGRESS" },
                                { "text": i18nBridge.tr("task_status_waiting", "Bekliyor"), "value": "WAITING" },
                                { "text": i18nBridge.tr("task_status_blocked", "Engellendi"), "value": "BLOCKED" },
                                { "text": i18nBridge.tr("task_status_done", "Tamamlandı"), "value": "DONE" },
                                { "text": i18nBridge.tr("task_status_cancelled", "İptal Edildi"), "value": "CANCELLED" }
                            ]
                        }

                        AppComboBox {
                            id: priorityCombo
                            label: i18nBridge.tr("label_priority", "Öncelik")
                            Layout.fillWidth: true
                            Layout.preferredWidth: 1
                            model: [
                                { "text": i18nBridge.tr("priority_low", "Düşük"), "value": "LOW" },
                                { "text": i18nBridge.tr("priority_medium", "Orta"), "value": "MEDIUM" },
                                { "text": i18nBridge.tr("priority_high", "Yüksek"), "value": "HIGH" },
                                { "text": i18nBridge.tr("priority_critical", "Kritik"), "value": "CRITICAL" }
                            ]
                        }

                        AppComboBox {
                            id: typeCombo
                            label: i18nBridge.tr("label_type", "Tip")
                            Layout.fillWidth: true
                            Layout.preferredWidth: 1
                            model: [
                                { "text": i18nBridge.tr("task_type_task", "Görev"), "value": "TASK" },
                                { "text": i18nBridge.tr("task_type_group", "Grup"), "value": "GROUP" },
                                { "text": i18nBridge.tr("task_type_bug", "Hata"), "value": "BUG" },
                                { "text": i18nBridge.tr("task_type_improvement", "İyileştirme"), "value": "IMPROVEMENT" },
                                { "text": i18nBridge.tr("task_type_research", "Araştırma"), "value": "RESEARCH" }
                            ]
                        }
                    }

                    // Checklist Bölümü
                    Text {
                        text: i18nBridge.tr("label_checklist", "Kontrol Listesi (Checklist)")
                        font.pixelSize: Theme.typography.sizeSmall
                        font.weight: Theme.typography.weightMedium
                        color: themeBridge.color("text_secondary")
                        Layout.topMargin: Theme.spacing.xs
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: Theme.spacing.sm

                        AppTextInput {
                            id: newChecklistInput
                            placeholder: i18nBridge.tr("task_checklist_placeholder", "Yeni kontrol maddesi ekle...")
                            Layout.fillWidth: true
                            onAccepted: addChecklistItem()
                        }

                        AppButton {
                            text: i18nBridge.tr("action_add", "Ekle")
                            btnVariant: "secondary"
                            Layout.preferredHeight: 38
                            Layout.alignment: Qt.AlignVCenter
                            onClicked: addChecklistItem()
                        }
                    }

                    // Eklenen Checklist Maddeleri Listesi
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: Theme.spacing.xs

                        Repeater {
                            model: root.checklistItems

                            Rectangle {
                                Layout.fillWidth: true
                                height: 32
                                radius: Theme.radius.small
                                color: themeBridge.color("surface_alt")

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.leftMargin: Theme.spacing.sm
                                    anchors.rightMargin: Theme.spacing.sm
                                    spacing: Theme.spacing.sm

                                    AppIcon {
                                        name: "check"
                                        size: 14
                                        color: Theme.accent(themeBridge.currentTheme)
                                    }

                                    Text {
                                        id: chkItemText
                                        text: modelData
                                        font.pixelSize: Theme.typography.sizeSmall
                                        color: themeBridge.color("text_primary")
                                        Layout.fillWidth: true
                                        elide: Text.ElideRight

                                        ToolTip.visible: chkHoverArea.containsMouse && chkItemText.truncated
                                        ToolTip.text: modelData
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
            }

            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: themeBridge.color("border")
            }

            // Alt Buton Çubuğu
            RowLayout {
                Layout.alignment: Qt.AlignHCenter
                spacing: Theme.spacing.md

                AppButton {
                    text: i18nBridge.tr("action_delete", "Sil")
                    btnVariant: "danger"
                    implicitWidth: 120
                    implicitHeight: 40
                    visible: taskViewModel ? taskViewModel.dialogMode === "edit" : false
                    onClicked: {
                        if (taskViewModel) {
                            taskViewModel.deleteTask(taskViewModel.dialogTaskId)
                            taskViewModel.closeDialog()
                        }
                    }
                }

                AppButton {
                    text: i18nBridge.tr("action_cancel", "İptal")
                    btnVariant: "secondary"
                    implicitWidth: 120
                    implicitHeight: 40
                    onClicked: taskViewModel.closeDialog()
                }

                AppButton {
                    text: i18nBridge.tr("action_save", "Kaydet")
                    btnVariant: "primary"
                    implicitWidth: 120
                    implicitHeight: 40
                    onClicked: {
                        if (taskViewModel) {
                            taskViewModel.saveTask({
                                "title": titleInput.text,
                                "description": descInput.text,
                                "status": statusCombo.selectedValue,
                                "priority": priorityCombo.selectedValue,
                                "task_type": typeCombo.selectedValue,
                                "checklist_items": root.checklistItems
                            })
                        }
                    }
                }
            }
        }
    }

    function addChecklistItem() {
        var txt = newChecklistInput.text.trim()
        if (txt.length > 0) {
            var arr = root.checklistItems.slice()
            arr.push(txt)
            root.checklistItems = arr
            newChecklistInput.text = ""
        }
    }
}
