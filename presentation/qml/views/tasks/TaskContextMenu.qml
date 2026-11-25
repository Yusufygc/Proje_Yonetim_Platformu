import QtQuick
import QtQuick.Controls

Menu {
    id: root
    property int taskId: 0

    MenuItem {
        text: i18nBridge.tr("task_add_child", "Alt Görev Ekle")
        onTriggered: {
            if (taskViewModel) taskDialogViewModel.openCreateDialog(root.taskId)
        }
    }

    MenuItem {
        text: i18nBridge.tr("action_edit", "Düzenle")
        onTriggered: {
            if (taskViewModel) taskDialogViewModel.openEditDialog(root.taskId)
        }
    }

    MenuSeparator {}

    MenuItem {
        text: i18nBridge.tr("action_copy_task", "Panoya Kopyala")
        onTriggered: {
            if (taskViewModel) taskViewModel.copyTaskToClipboard(root.taskId)
        }
    }

    MenuItem {
        text: i18nBridge.tr("action_duplicate_task", "Görevi Çoğalt")
        onTriggered: {
            if (taskViewModel) taskViewModel.duplicateTask(root.taskId)
        }
    }

    MenuSeparator {}

    MenuItem {
        text: i18nBridge.tr("action_delete", "Sil")
        onTriggered: {
            if (taskViewModel) taskViewModel.deleteTask(root.taskId)
        }
    }
}
