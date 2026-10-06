import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../components"
import "../theme"

Rectangle {
    id: dialogRoot

    anchors.fill: parent
    color: Qt.rgba(0, 0, 0, 0.65)
    visible: projectViewModel ? projectViewModel.isDialogOpen : false
    z: 9999

    MouseArea {
        anchors.fill: parent
        onClicked: { /* modal dışı tıklamayı engeller */ }
    }

    Shortcut {
        sequence: "Escape"
        enabled: dialogRoot.visible
        onActivated: projectViewModel.closeDialog()
    }

    AppCard {
        id: formCard
        width: Math.min(680, parent.width - 48)
        height: Math.min(660, parent.height - 48)
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
                    name: "folder"
                    size: 22
                    color: Theme.accent(themeBridge.currentTheme)
                }

                Text {
                    text: {
                        if (!projectViewModel) return ""
                        return projectViewModel.dialogMode === "edit"
                            ? i18nBridge.tr("dialog_edit_project", "Projeyi Düzenle")
                            : i18nBridge.tr("dialog_new_project", "Yeni Proje Oluştur")
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
                    onClicked: projectViewModel.closeDialog()
                }
            }

            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: themeBridge.color("border")
            }

            // Form Kaydırma Alanı
            ScrollView {
                id: projScroll
                Layout.fillWidth: true
                Layout.fillHeight: true
                contentWidth: availableWidth
                clip: true

                ScrollBar.vertical: AppScrollBar { }

                ColumnLayout {
                    width: projScroll.availableWidth - 16
                    spacing: Theme.spacing.md

                    AppTextInput {
                        id: titleInput
                        label: i18nBridge.tr("field_project_title", "Proje Başlığı *")
                        placeholder: i18nBridge.tr("project_dialog_title_placeholder", "Projenizin adını yazın...")
                        Layout.fillWidth: true
                        showVoiceInput: true
                    }

                    AppTextInput {
                        id: descInput
                        label: i18nBridge.tr("field_description", "Açıklama")
                        placeholder: i18nBridge.tr("project_dialog_short_desc_placeholder", "Projenin kapsamını ve amacını açıklayın...")
                        isTextArea: true
                        Layout.fillWidth: true
                        showVoiceInput: true
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: Theme.spacing.md

                        AppComboBox {
                            id: statusCombo
                            label: i18nBridge.tr("field_status", "Durum")
                            Layout.fillWidth: true
                            Layout.preferredWidth: 1
                            model: [
                                { "text": i18nBridge.tr("status_planned", "Planlandı"), "value": "PLANNED" },
                                { "text": i18nBridge.tr("status_active", "Aktif"), "value": "ACTIVE" },
                                { "text": i18nBridge.tr("status_on_hold", "Beklemede"), "value": "ON_HOLD" },
                                { "text": i18nBridge.tr("status_blocked", "Engellendi"), "value": "BLOCKED" },
                                { "text": i18nBridge.tr("status_completed", "Tamamlandı"), "value": "COMPLETED" },
                                { "text": i18nBridge.tr("status_cancelled", "İptal Edildi"), "value": "CANCELLED" }
                            ]
                        }

                        AppComboBox {
                            id: priorityCombo
                            label: i18nBridge.tr("field_priority", "Öncelik")
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
                            id: healthCombo
                            label: i18nBridge.tr("field_health", "Sağlık")
                            Layout.fillWidth: true
                            Layout.preferredWidth: 1
                            model: [
                                { "text": i18nBridge.tr("health_good", "Yolunda"), "value": "GOOD" },
                                { "text": i18nBridge.tr("health_at_risk", "Riskli"), "value": "AT_RISK" },
                                { "text": i18nBridge.tr("health_blocked", "Tıkandı"), "value": "BLOCKED" },
                                { "text": i18nBridge.tr("health_unknown", "Belirsiz"), "value": "UNKNOWN" }
                            ]
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: Theme.spacing.md

                        AppTextInput {
                            id: typeInput
                            Layout.fillWidth: true
                            Layout.preferredWidth: 1
                            label: i18nBridge.tr("field_project_type", "Proje Türü")
                            placeholder: "Yazılım, Tasarım, Araştırma..."
                        }

                        AppTextInput {
                            id: audienceInput
                            Layout.fillWidth: true
                            Layout.preferredWidth: 1
                            label: i18nBridge.tr("field_target_audience", "Hedef Kitle")
                            placeholder: "Hedef kullanıcı kitlesi"
                        }
                    }

                    AppTextInput {
                        id: problemInput
                        label: i18nBridge.tr("field_problem", "Problem Tanımı")
                        placeholder: "Bu proje hangi sorunu çözüyor?"
                        Layout.fillWidth: true
                        showVoiceInput: true
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: Theme.spacing.md

                        AppTextInput {
                            id: githubInput
                            Layout.fillWidth: true
                            Layout.preferredWidth: 1
                            label: "GitHub Deposu"
                            placeholder: "https://github.com/..."
                        }

                        AppTextInput {
                            id: localPathInput
                            Layout.fillWidth: true
                            Layout.preferredWidth: 1
                            label: "Yerel Klasör Yolu"
                            placeholder: "C:/projeler/..."
                        }
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: themeBridge.color("border")
            }

            // Alt Butonlar
            RowLayout {
                Layout.alignment: Qt.AlignHCenter
                spacing: Theme.spacing.md

                AppButton {
                    text: i18nBridge.tr("action_delete", "Sil")
                    btnVariant: "danger"
                    implicitWidth: 120
                    implicitHeight: 40
                    visible: projectViewModel ? projectViewModel.dialogMode === "edit" : false
                    onClicked: {
                        if (projectViewModel && projectViewModel.selectedProject) {
                            projectViewModel.deleteProject(projectViewModel.selectedProject.id)
                            projectViewModel.closeDialog()
                        }
                    }
                }

                AppButton {
                    btnVariant: "secondary"
                    text: i18nBridge.tr("btn_cancel", "İptal")
                    implicitWidth: 120
                    implicitHeight: 40
                    onClicked: projectViewModel.closeDialog()
                }

                AppButton {
                    btnVariant: "primary"
                    text: i18nBridge.tr("action_save", "Kaydet")
                    implicitWidth: 120
                    implicitHeight: 40
                    onClicked: {
                        var data = {
                            "title": titleInput.text,
                            "description": descInput.text,
                            "status": statusCombo.selectedValue || "PLANNED",
                            "priority": priorityCombo.selectedValue || "MEDIUM",
                            "health": healthCombo.selectedValue || "GOOD",
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
        if (visible && projectViewModel) {
            if (projectViewModel.dialogMode === "edit" && projectViewModel.selectedProject) {
                var p = projectViewModel.selectedProject;
                titleInput.text = p.title || "";
                descInput.text = p.description || "";
                typeInput.text = p.project_type || "Yazılım";
                audienceInput.text = p.target_audience || "";
                problemInput.text = p.problem_statement || "";
                githubInput.text = p.github_repo || "";
                localPathInput.text = p.local_path || "";
                statusCombo.selectedValue = p.status || "PLANNED";
                priorityCombo.selectedValue = p.priority || "MEDIUM";
                healthCombo.selectedValue = p.health || "GOOD";
            } else {
                titleInput.text = "";
                descInput.text = "";
                typeInput.text = "Yazılım";
                audienceInput.text = "";
                problemInput.text = "";
                githubInput.text = "";
                localPathInput.text = "";
                statusCombo.selectedValue = "PLANNED";
                priorityCombo.selectedValue = "MEDIUM";
                healthCombo.selectedValue = "GOOD";
            }
        }
    }
}
