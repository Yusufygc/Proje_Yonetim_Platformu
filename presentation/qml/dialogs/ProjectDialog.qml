import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"

Rectangle {
    id: dialogRoot

    anchors.fill: parent
    color: Qt.rgba(0, 0, 0, 0.65)
    visible: projectViewModel.isDialogOpen
    z: 9999

    MouseArea {
        anchors.fill: parent
        onClicked: projectViewModel.closeDialog()
    }

    Shortcut {
        sequence: "Escape"
        enabled: dialogRoot.visible
        onActivated: projectViewModel.closeDialog()
    }

    Rectangle {
        id: formCard
        width: Math.min(680, parent.width - 48)
        height: Math.min(640, parent.height - 48)
        anchors.centerIn: parent
        radius: 12
        color: themeBridge.surface
        border.width: 1
        border.color: themeBridge.accentStart

        MouseArea {
            anchors.fill: parent
            // prevent click outside
        }

        Column {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 14

            // Başlık Çubuğu
            Row {
                width: parent.width
                spacing: 8

                Text {
                    text: projectViewModel.dialogMode === "edit" ?
                        i18nBridge.tr("dialog_edit_project", "Projeyi Düzenle") :
                        i18nBridge.tr("dialog_new_project", "Yeni Proje Oluştur")
                    font.pixelSize: 18
                    font.weight: Font.Bold
                    color: themeBridge.textPrimary
                    anchors.verticalCenter: parent.verticalCenter
                    width: parent.width - 40
                }

                AppButton {
                    variant: "ghost"
                    text: "✕"
                    implicitWidth: 32
                    implicitHeight: 32
                    onClicked: projectViewModel.closeDialog()
                    anchors.verticalCenter: parent.verticalCenter
                }
            }

            // Form Kaydırma Alanı
            ScrollView {
                width: parent.width
                height: formCard.height - 120
                contentWidth: availableWidth
                clip: true

                Column {
                    width: parent.width
                    spacing: 12

                    AppTextInput {
                        id: titleInput
                        label: i18nBridge.tr("field_project_title", "Proje Başlığı *")
                        placeholder: "Projenizin adını yazın..."
                        showVoiceInput: true
                    }

                    AppTextInput {
                        id: descInput
                        label: i18nBridge.tr("field_description", "Açıklama")
                        placeholder: "Projenin kapsamını ve amacını açıklayın..."
                        isTextArea: true
                        showVoiceInput: true
                    }

                    Row {
                        width: parent.width
                        spacing: 12

                        AppComboBox {
                            id: statusCombo
                            label: i18nBridge.tr("field_status", "Durum")
                            width: (parent.width - 24) / 3
                            model: ["PLANNED", "ACTIVE", "ON_HOLD", "BLOCKED", "COMPLETED", "CANCELLED"]
                        }

                        AppComboBox {
                            id: priorityCombo
                            label: i18nBridge.tr("field_priority", "Öncelik")
                            width: (parent.width - 24) / 3
                            model: ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
                        }

                        AppComboBox {
                            id: healthCombo
                            label: i18nBridge.tr("field_health", "Sağlık")
                            width: (parent.width - 24) / 3
                            model: ["GOOD", "AT_RISK", "BLOCKED", "UNKNOWN"]
                        }
                    }

                    Row {
                        width: parent.width
                        spacing: 12

                        AppTextInput {
                            id: typeInput
                            width: (parent.width - 12) / 2
                            label: i18nBridge.tr("field_project_type", "Proje Türü")
                            placeholder: "Yazılım, Tasarım, Araştırma..."
                        }

                        AppTextInput {
                            id: audienceInput
                            width: (parent.width - 12) / 2
                            label: i18nBridge.tr("field_target_audience", "Hedef Kitle")
                            placeholder: "Hedef kullanıcı kitlesi"
                        }
                    }

                    AppTextInput {
                        id: problemInput
                        label: i18nBridge.tr("field_problem", "Problem Tanımı")
                        placeholder: "Bu proje hangi sorunu çözüyor?"
                    }

                    Row {
                        width: parent.width
                        spacing: 12

                        AppTextInput {
                            id: githubInput
                            width: (parent.width - 12) / 2
                            label: "GitHub Deposu"
                            placeholder: "https://github.com/..."
                        }

                        AppTextInput {
                            id: localPathInput
                            width: (parent.width - 12) / 2
                            label: "Yerel Klasör Yolu"
                            placeholder: "C:/projeler/..."
                        }
                    }
                }
            }

            // Alt Butonlar
            Row {
                anchors.right: parent.right
                spacing: 12

                AppButton {
                    variant: "secondary"
                    text: i18nBridge.tr("btn_cancel", "İptal")
                    onClicked: projectViewModel.closeDialog()
                }

                AppButton {
                    variant: "primary"
                    text: i18nBridge.tr("btn_save", "Kaydet")
                    onClicked: {
                        var data = {
                            "title": titleInput.text,
                            "description": descInput.text,
                            "status": statusCombo.currentValue,
                            "priority": priorityCombo.currentValue,
                            "health": healthCombo.currentValue,
                            "project_type": typeInput.text,
                            "target_audience": audienceInput.text,
                            "problem_statement": problemInput.text,
                            "github_repo": githubInput.text,
                            "local_path": localPathInput.text
                        };
                        projectViewModel.saveProject(data);
                    }
                }
            }
        }
    }

    onVisibleChanged: {
        if (visible) {
            if (projectViewModel.dialogMode === "edit" && projectViewModel.selectedProject) {
                var p = projectViewModel.selectedProject;
                titleInput.text = p.title || "";
                descInput.text = p.description || "";
                typeInput.text = p.project_type || "";
                audienceInput.text = p.target_audience || "";
                problemInput.text = p.problem_statement || "";
                githubInput.text = p.github_repo || "";
                localPathInput.text = p.local_path || "";
            } else {
                titleInput.text = "";
                descInput.text = "";
                typeInput.text = "Yazılım";
                audienceInput.text = "";
                problemInput.text = "";
                githubInput.text = "";
                localPathInput.text = "";
            }
        }
    }
}
