import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../components"
import "../../theme"

// Görevler ekranı araç çubuğu: proje seçici, arama, filtreler ve ana görev ekleme.
RowLayout {
    id: root

    Layout.fillWidth: true
    spacing: Theme.spacing.md

    // Proje Seçici Dropdown
    AppComboBox {
        id: projectSelector
        Layout.preferredWidth: 240
        model: {
            if (!taskViewModel || !taskViewModel.projects) return []
            var list = []
            for (var i = 0; i < taskViewModel.projects.length; i++) {
                var p = taskViewModel.projects[i]
                list.push({ "text": p.title, "value": p.id })
            }
            return list
        }
        onSelectedValueChanged: {
            if (taskViewModel && selectedValue !== undefined && selectedValue !== 0) {
                taskViewModel.selectProject(selectedValue)
            }
        }
    }

    // Arama Kutusu
    AppTextInput {
        id: searchInput
        placeholder: i18nBridge.tr("tasks_search_placeholder", "Görevlerde ara...")
        Layout.fillWidth: true
        onTextChanged: {
            if (taskViewModel) taskViewModel.setSearchQuery(text)
        }
    }

    // Durum Filtresi
    AppComboBox {
        id: statusFilterCombo
        Layout.preferredWidth: 160
        model: [
            { "text": i18nBridge.tr("filter_all_status", "Tüm Durumlar"), "value": "ALL" },
            { "text": i18nBridge.tr("task_status_todo", "Yapılacak"), "value": "TODO" },
            { "text": i18nBridge.tr("task_status_in_progress", "Devam Ediyor"), "value": "IN_PROGRESS" },
            { "text": i18nBridge.tr("task_status_waiting", "Bekliyor"), "value": "WAITING" },
            { "text": i18nBridge.tr("task_status_blocked", "Engellendi"), "value": "BLOCKED" },
            { "text": i18nBridge.tr("task_status_done", "Tamamlandı"), "value": "DONE" }
        ]
        onSelectedValueChanged: {
            if (taskViewModel && selectedValue) {
                taskViewModel.setStatusFilter(selectedValue)
            }
        }
    }

    // Öncelik Filtresi
    AppComboBox {
        id: priorityFilterCombo
        Layout.preferredWidth: 150
        model: [
            { "text": i18nBridge.tr("filter_all_priority", "Tüm Öncelikler"), "value": "ALL" },
            { "text": i18nBridge.tr("priority_low", "Düşük"), "value": "LOW" },
            { "text": i18nBridge.tr("priority_medium", "Orta"), "value": "MEDIUM" },
            { "text": i18nBridge.tr("priority_high", "Yüksek"), "value": "HIGH" },
            { "text": i18nBridge.tr("priority_critical", "Kritik"), "value": "CRITICAL" }
        ]
        onSelectedValueChanged: {
            if (taskViewModel && selectedValue) {
                taskViewModel.setPriorityFilter(selectedValue)
            }
        }
    }

    // Tip Filtresi
    AppComboBox {
        id: typeFilterCombo
        Layout.preferredWidth: 150
        model: [
            { "text": i18nBridge.tr("filter_all_types", "Tüm Tipler"), "value": "ALL" },
            { "text": i18nBridge.tr("task_type_task", "Görev"), "value": "TASK" },
            { "text": i18nBridge.tr("task_type_group", "Grup"), "value": "GROUP" },
            { "text": i18nBridge.tr("task_type_bug", "Hata"), "value": "BUG" },
            { "text": i18nBridge.tr("task_type_improvement", "İyileştirme"), "value": "IMPROVEMENT" },
            { "text": i18nBridge.tr("task_type_research", "Araştırma"), "value": "RESEARCH" },
            { "text": i18nBridge.tr("task_type_documentation", "Dokümantasyon"), "value": "DOCUMENTATION" },
            { "text": i18nBridge.tr("task_type_design", "Tasarım"), "value": "DESIGN" },
            { "text": i18nBridge.tr("task_type_test", "Test"), "value": "TEST" },
            { "text": i18nBridge.tr("task_type_review", "İnceleme"), "value": "REVIEW" }
        ]
        onSelectedValueChanged: {
            if (taskViewModel && selectedValue) {
                taskViewModel.setTypeFilter(selectedValue)
            }
        }
    }

    // "+ Ana Görev Ekle" Butonu
    AppButton {
        text: i18nBridge.tr("task_add_root_plain", "Ana Görev Ekle")
        iconName: "plus"
        btnVariant: "primary"
        onClicked: {
            if (taskViewModel) taskDialogViewModel.openCreateDialog(0)
        }
    }
}
