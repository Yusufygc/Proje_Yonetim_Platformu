import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../components"
import "../../theme"

// Hızlı görev ekleme: yazarak ya da mikrofonla dikte ederek tek satırda görev oluşturur.
// Bir görev seçiliyse yeni görev onun altına (alt görev), seçili değilse proje köküne eklenir.
RowLayout {
    id: root

    readonly property bool hasProject: taskViewModel && taskViewModel.selectedProjectId > 0
    readonly property bool hasSelection: taskViewModel && taskViewModel.selectedTaskId > 0

    Layout.fillWidth: true
    spacing: Theme.spacing.md

    function submit() {
        if (!hasProject || quickInput.text.trim() === "") return
        taskViewModel.quickAddTask(quickInput.text)
        quickInput.text = ""
    }

    AppTextInput {
        id: quickInput
        Layout.fillWidth: true
        showVoiceInput: true
        readOnly: !root.hasProject
        placeholder: root.hasSelection
            ? i18nBridge.tr("task_quick_add_placeholder", "Seçili görevin altına hızlı görev ekle...")
            : i18nBridge.tr("task_quick_add_root_placeholder", "Projeye hızlıca ana görev ekle...")
        onAccepted: root.submit()
    }

    AppButton {
        Layout.alignment: Qt.AlignVCenter
        iconName: "plus"
        text: i18nBridge.tr("task_quick_add_button", "Hızlı Ekle")
        btnVariant: "secondary"
        enabled: root.hasProject && quickInput.text.trim() !== ""
        onClicked: root.submit()
    }
}
