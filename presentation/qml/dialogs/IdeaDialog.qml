import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"
import "../theme"

Rectangle {
    id: root

    visible: ideaViewModel ? ideaViewModel.isDialogOpen : false
    anchors.fill: parent
    color: "#80000000"
    z: 999

    MouseArea {
        anchors.fill: parent
        onClicked: { /* modal diyalog dışı tıklamayı engeller */ }
    }

    Connections {
        target: ideaViewModel
        function onDialogStateChanged() {
            if (ideaViewModel && ideaViewModel.isDialogOpen) {
                var init = ideaViewModel.dialogInitialData
                titleInput.text = init.title || ""
                problemInput.text = init.problem || ""
                solutionInput.text = init.solution || ""
                targetUserInput.text = init.target_user || ""
                notesInput.text = init.notes || ""
                sourceLinkInput.text = init.source_link || ""
                statusCombo.selectedValue = init.status || "RAW"
                priorityCombo.selectedValue = init.priority || "MEDIUM"
            }
        }
    }

    AppCard {
        id: dialogCard
        width: Math.min(parent.width - 48, 620)
        height: Math.min(parent.height - 48, 700)
        anchors.centerIn: parent

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: Theme.spacing.xl
            spacing: Theme.spacing.md

            // Başlık
            RowLayout {
                Layout.fillWidth: true
                spacing: Theme.spacing.sm

                AppIcon {
                    name: "ideas"
                    size: 22
                    color: Theme.accent(themeBridge.currentTheme)
                }

                Text {
                    text: {
                        if (!ideaViewModel) return ""
                        return ideaViewModel.dialogMode === "edit"
                            ? i18nBridge.tr("idea_dialog_edit_title", "Fikri Düzenle")
                            : i18nBridge.tr("idea_dialog_new_title", "Yeni Fikir Ekle")
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
                    onClicked: ideaViewModel.closeDialog()
                }
            }

            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: themeBridge.color("border")
            }

            // Form Kaydırma Alanı
            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true

                ColumnLayout {
                    width: parent.width - 12
                    spacing: Theme.spacing.md

                    // Başlık
                    AppTextInput {
                        id: titleInput
                        label: i18nBridge.tr("idea_dialog_title_label", "Fikir Başlığı *")
                        placeholder: i18nBridge.tr("idea_dialog_title_placeholder", "Örn: Yeni mobil uygulama fikri...")
                        Layout.fillWidth: true
                    }

                    // Durum ve Öncelik Yan Yana
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: Theme.spacing.md

                        AppComboBox {
                            id: statusCombo
                            label: i18nBridge.tr("label_status", "Durum")
                            Layout.fillWidth: true
                            model: [
                                { "text": i18nBridge.tr("idea_status_raw", "Ham Fikir"), "value": "RAW" },
                                { "text": i18nBridge.tr("idea_status_reviewing", "İnceleniyor"), "value": "REVIEWING" },
                                { "text": i18nBridge.tr("idea_status_validating", "Doğrulanıyor"), "value": "VALIDATING" },
                                { "text": i18nBridge.tr("idea_status_converted", "Projeye Dönüştürüldü"), "value": "CONVERTED" },
                                { "text": i18nBridge.tr("idea_status_deferred", "Ertelendi"), "value": "DEFERRED" },
                                { "text": i18nBridge.tr("idea_status_rejected", "Reddedildi"), "value": "REJECTED" }
                            ]
                        }

                        AppComboBox {
                            id: priorityCombo
                            label: i18nBridge.tr("label_priority", "Öncelik")
                            Layout.fillWidth: true
                            model: [
                                { "text": i18nBridge.tr("priority_low", "Düşük"), "value": "LOW" },
                                { "text": i18nBridge.tr("priority_medium", "Orta"), "value": "MEDIUM" },
                                { "text": i18nBridge.tr("priority_high", "Yüksek"), "value": "HIGH" },
                                { "text": i18nBridge.tr("priority_critical", "Kritik"), "value": "CRITICAL" }
                            ]
                        }
                    }

                    // Hedef Kullanıcı
                    AppTextInput {
                        id: targetUserInput
                        label: i18nBridge.tr("label_target_user", "Hedef Kullanıcı")
                        placeholder: i18nBridge.tr("idea_dialog_target_user_placeholder", "Kim için?")
                        Layout.fillWidth: true
                    }

                    // Problem
                    AppTextInput {
                        id: problemInput
                        label: i18nBridge.tr("idea_dialog_problem_label", "Çözülen Problem")
                        placeholder: i18nBridge.tr("idea_dialog_problem_placeholder", "Bu fikir hangi problemi çözüyor?")
                        isTextArea: true
                        Layout.fillWidth: true
                    }

                    // Çözüm
                    AppTextInput {
                        id: solutionInput
                        label: i18nBridge.tr("idea_dialog_solution_label", "Önerilen Çözüm")
                        placeholder: i18nBridge.tr("idea_dialog_solution_placeholder", "Önerdiğiniz çözüm detayları...")
                        isTextArea: true
                        Layout.fillWidth: true
                    }

                    // Notlar
                    AppTextInput {
                        id: notesInput
                        label: i18nBridge.tr("label_notes", "Notlar")
                        placeholder: i18nBridge.tr("idea_dialog_notes_placeholder", "Ek notlar...")
                        isTextArea: true
                        Layout.fillWidth: true
                    }

                    // Kaynak URL
                    AppTextInput {
                        id: sourceLinkInput
                        label: i18nBridge.tr("label_source_url", "Kaynak URL")
                        placeholder: "https://..."
                        Layout.fillWidth: true
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
                Layout.fillWidth: true
                spacing: Theme.spacing.sm

                AppButton {
                    text: i18nBridge.tr("action_delete", "Sil")
                    btnVariant: "danger"
                    visible: ideaViewModel ? ideaViewModel.dialogMode === "edit" : false
                    onClicked: {
                        if (ideaViewModel) {
                            ideaViewModel.deleteIdea(ideaViewModel.dialogIdeaId)
                            ideaViewModel.closeDialog()
                        }
                    }
                }

                Item { Layout.fillWidth: true }

                AppButton {
                    text: i18nBridge.tr("action_cancel", "İptal")
                    btnVariant: "secondary"
                    onClicked: ideaViewModel.closeDialog()
                }

                AppButton {
                    text: i18nBridge.tr("action_save", "Kaydet")
                    btnVariant: "primary"
                    onClicked: {
                        if (ideaViewModel) {
                            ideaViewModel.saveIdea({
                                "title": titleInput.text,
                                "problem": problemInput.text,
                                "solution": solutionInput.text,
                                "target_user": targetUserInput.text,
                                "status": statusCombo.selectedValue,
                                "priority": priorityCombo.selectedValue,
                                "notes": notesInput.text,
                                "source_link": sourceLinkInput.text
                            })
                        }
                    }
                }
            }
        }
    }
}
