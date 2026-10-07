import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../../components"
import "../../../theme"

// Proje görevleri sekmesi (hızlı ekleme ve liste).
ColumnLayout {
    id: root

    spacing: 8

    RowLayout {
        Layout.fillWidth: true
        spacing: 8

        Text {
            text: i18nBridge.tr("tab_tasks_title", "Proje Görevleri:")
            font.pixelSize: 13
            font.weight: Font.DemiBold
            color: themeBridge.color("text_secondary")
        }

        Text {
            text: "(" + (projectViewModel.selectedTasks ? projectViewModel.selectedTasks.length : 0) + ")"
            font.pixelSize: 12
            color: themeBridge.color("text_muted")
        }

        Item { Layout.fillWidth: true }

        AppButton {
            btnVariant: "secondary"
            iconName: "external-link"
            text: i18nBridge.tr("tab_tasks_wbs_page", "WBS Sayfasında Aç")
            implicitHeight: 28
            onClicked: navBridge.navigateTo("tasks")
        }
    }

    // Hızlı Görev Ekleme Satırı
    RowLayout {
        Layout.fillWidth: true
        spacing: 8

        AppTextInput {
            id: quickTaskInput
            placeholder: i18nBridge.tr("placeholder_new_task", "Yeni görev başlığı yazın...")
            Layout.fillWidth: true
            inputHeight: 36
            onAccepted: {
                if (quickTaskInput.text.trim()) {
                    projectViewModel.addTask(quickTaskInput.text.trim());
                    quickTaskInput.text = "";
                }
            }
        }

        AppButton {
            btnVariant: "primary"
            iconName: "plus"
            text: i18nBridge.tr("action_add", "Ekle")
            implicitHeight: 36
            onClicked: {
                if (quickTaskInput.text.trim()) {
                    projectViewModel.addTask(quickTaskInput.text.trim());
                    quickTaskInput.text = "";
                }
            }
        }
    }

    ListView {
        id: projectTasksList
        Layout.fillWidth: true
        Layout.fillHeight: true
        clip: true
        spacing: 6
        boundsBehavior: Flickable.StopAtBounds
        model: projectViewModel.selectedTasks

        ScrollBar.vertical: AppScrollBar { }

        delegate: Rectangle {
            width: projectTasksList.width - 14
            height: 38
            radius: 6
            color: themeBridge.surfaceAlt
            border.color: themeBridge.border
            border.width: 1

            RowLayout {
                anchors.leftMargin: (modelData.parent_id > 0 ? 24 : 10)
                anchors.rightMargin: 10
                spacing: 8

                // Durum Checkbox'ı
                Rectangle {
                    width: 18
                    height: 18
                    radius: 4
                    color: modelData.is_done ? themeBridge.color("success") : "transparent"
                    border.color: modelData.is_done ? themeBridge.color("success") : themeBridge.color("border")
                    border.width: 1.5

                    AppIcon {
                        anchors.centerIn: parent
                        name: "check"
                        size: 12
                        color: "#FFFFFF"
                        visible: modelData.is_done
                    }

                    MouseArea {
                        cursorShape: Qt.PointingHandCursor
                        onClicked: projectViewModel.toggleTaskStatus(modelData.id)
                    }
                }

                // Alt görev oku
                Text {
                    visible: modelData.parent_id > 0
                    text: "↳"
                    font.pixelSize: 12
                    color: themeBridge.color("text_muted")
                }

                // Görev Başlığı
                Text {
                    text: modelData.title
                    font.pixelSize: 12
                    font.strikeout: modelData.is_done
                    font.weight: Font.Medium
                    color: modelData.is_done ? themeBridge.color("text_muted") : themeBridge.color("text_primary")
                    Layout.fillWidth: true
                    elide: Text.ElideRight
                }

                // Öncelik Rozeti
                AppBadge {
                    visible: !!modelData.priority
                    text: {
                        var p = (modelData.priority || "MEDIUM").toUpperCase();
                        switch (p) {
                            case "URGENT": return i18nBridge.tr("priority_urgent", "Acil");
                            case "HIGH": return i18nBridge.tr("priority_high", "Yüksek");
                            case "MEDIUM": return i18nBridge.tr("priority_medium", "Orta");
                            case "LOW": return i18nBridge.tr("priority_low", "Düşük");
                            default: return p;
                        }
                    }
                    variant: {
                        var p = (modelData.priority || "MEDIUM").toUpperCase();
                        if (p === "URGENT" || p === "HIGH") return "danger";
                        if (p === "MEDIUM") return "warning";
                        return "neutral";
                    }
                    size: "sm"
                }

                // Durum Rozeti
                AppBadge {
                    text: {
                        var st = (modelData.status || "TODO").toUpperCase();
                        switch (st) {
                            case "DONE": return i18nBridge.tr("status_done", "Tamamlandı");
                            case "IN_PROGRESS": return i18nBridge.tr("status_in_progress", "Sürüyor");
                            case "BLOCKED": return i18nBridge.tr("status_blocked", "Engellendi");
                            case "REVIEW": return i18nBridge.tr("status_review", "İncelemede");
                            default: return i18nBridge.tr("status_todo", "Yapılacak");
                        }
                    }
                    variant: modelData.is_done ? "success" : (modelData.status === "IN_PROGRESS" ? "info" : "secondary")
                    size: "sm"
                }

                // Vade Tarihi
                Text {
                    visible: !!modelData.due_date
                    text: modelData.due_date || ""
                    font.pixelSize: 11
                    color: themeBridge.color("text_muted")
                }

                // Silme Butonu
                AppButton {
                    iconName: "trash-2"
                    btnVariant: "secondary"
                    implicitWidth: 22
                    implicitHeight: 22
                    onClicked: projectViewModel.deleteTask(modelData.id)
                }
            }
        }

        // Boş Durum
        Text {
            anchors.centerIn: parent
            visible: !projectViewModel.selectedTasks || projectViewModel.selectedTasks.length === 0
            text: i18nBridge.tr("no_tasks", "Bu projede henüz kayıtlı görev yok.")
            font.pixelSize: 12
            color: themeBridge.color("text_muted")
        }
    }
}
