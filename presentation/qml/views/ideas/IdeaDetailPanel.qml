import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../components"
import "../../theme"

AppCard {
    id: root

    property var idea: ideaViewModel ? ideaViewModel.selectedIdea : ({})
    property bool hasIdea: Boolean(idea && idea.id !== undefined && idea.id !== 0)

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacing.xl
        spacing: Theme.spacing.lg

        // Fikir Seçili Değilse Boş Durum
        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true
            visible: !root.hasIdea

            ColumnLayout {
                anchors.centerIn: parent
                spacing: Theme.spacing.md

                AppIcon {
                    name: "ideas"
                    size: 48
                    color: themeBridge.color("text_muted")
                    Layout.alignment: Qt.AlignHCenter
                }

                Text {
                    text: i18nBridge.tr("idea_detail_select_prompt", "Detayları görüntülemek için bir fikir seçin")
                    font.pixelSize: Theme.typography.sizeH3
                    color: themeBridge.color("text_secondary")
                    Layout.alignment: Qt.AlignHCenter
                }
            }
        }

        // Fikir Detayları
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: Theme.spacing.md
            visible: root.hasIdea

            // Başlık & Rozetler & Eylemler
            RowLayout {
                Layout.fillWidth: true
                spacing: Theme.spacing.md

                Text {
                    text: root.idea.title || ""
                    font.pixelSize: Theme.typography.sizeH2
                    font.weight: Theme.typography.weightBold
                    color: themeBridge.color("text_primary")
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap
                }

                StatusIndicator {
                    status: root.idea.status || "RAW"
                }

                AppBadge {
                    text: {
                        var p = root.idea.priority || "MEDIUM"
                        if (p === "CRITICAL") return i18nBridge.tr("priority_critical", "Kritik")
                        if (p === "HIGH") return i18nBridge.tr("priority_high", "Yüksek")
                        if (p === "LOW") return i18nBridge.tr("priority_low", "Düşük")
                        return i18nBridge.tr("priority_medium", "Orta")
                    }
                    variant: {
                        var pr = root.idea.priority || "MEDIUM"
                        if (pr === "CRITICAL") return "danger"
                        if (pr === "HIGH") return "warning"
                        if (pr === "LOW") return "neutral"
                        return "info"
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: themeBridge.color("border")
            }

            // İçerik Kaydırma Alanı
            ScrollView {
                id: detailScroll
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true

                ScrollBar.vertical: AppScrollBar {
                    id: detailScrollBar
                }

                ColumnLayout {
                    width: detailScroll.availableWidth - 16
                    spacing: Theme.spacing.lg

                    // Hedef Kullanıcı
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: Theme.spacing.xs
                        visible: Boolean(root.idea && root.idea.targetUser && root.idea.targetUser.length > 0)

                        Text {
                            text: i18nBridge.tr("label_target_user", "Hedef Kullanıcı")
                            font.pixelSize: Theme.typography.sizeSmall
                            font.weight: Theme.typography.weightSemiBold
                            color: themeBridge.color("text_secondary")
                        }

                        Text {
                            text: root.idea.targetUser || ""
                            font.pixelSize: Theme.typography.sizeBody
                            color: themeBridge.color("text_primary")
                            wrapMode: Text.Wrap
                            Layout.fillWidth: true
                        }
                    }

                    // Problem
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: Theme.spacing.xs
                        visible: Boolean(root.idea && root.idea.problem && root.idea.problem.length > 0)

                        Text {
                            text: i18nBridge.tr("idea_dialog_problem_label", "Çözülen Problem")
                            font.pixelSize: Theme.typography.sizeSmall
                            font.weight: Theme.typography.weightSemiBold
                            color: themeBridge.color("text_secondary")
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            implicitHeight: probText.implicitHeight + 20
                            radius: Theme.radius.small
                            color: themeBridge.color("surface_alt")
                            border.color: themeBridge.color("border")
                            border.width: 1

                            Text {
                                id: probText
                                anchors.left: parent.left
                                anchors.right: parent.right
                                anchors.top: parent.top
                                anchors.margins: 10
                                text: root.idea.problem || ""
                                font.pixelSize: Theme.typography.sizeBody
                                color: themeBridge.color("text_primary")
                                wrapMode: Text.Wrap
                            }
                        }
                    }

                    // Çözüm
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: Theme.spacing.xs
                        visible: Boolean(root.idea && root.idea.solution && root.idea.solution.length > 0)

                        Text {
                            text: i18nBridge.tr("idea_dialog_solution_label", "Önerilen Çözüm")
                            font.pixelSize: Theme.typography.sizeSmall
                            font.weight: Theme.typography.weightSemiBold
                            color: themeBridge.color("text_secondary")
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            implicitHeight: solText.implicitHeight + 20
                            radius: Theme.radius.small
                            color: themeBridge.color("surface_alt")
                            border.color: themeBridge.color("border")
                            border.width: 1

                            Text {
                                id: solText
                                anchors.left: parent.left
                                anchors.right: parent.right
                                anchors.top: parent.top
                                anchors.margins: 10
                                text: root.idea.solution || ""
                                font.pixelSize: Theme.typography.sizeBody
                                color: themeBridge.color("text_primary")
                                wrapMode: Text.Wrap
                            }
                        }
                    }

                    // Notlar
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: Theme.spacing.xs
                        visible: Boolean(root.idea && root.idea.notes && root.idea.notes.length > 0)

                        Text {
                            text: i18nBridge.tr("label_notes", "Notlar")
                            font.pixelSize: Theme.typography.sizeSmall
                            font.weight: Theme.typography.weightSemiBold
                            color: themeBridge.color("text_secondary")
                        }

                        Text {
                            text: root.idea.notes || ""
                            font.pixelSize: Theme.typography.sizeBody
                            color: themeBridge.color("text_primary")
                            wrapMode: Text.Wrap
                            Layout.fillWidth: true
                        }
                    }

                    // Kaynak URL
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: Theme.spacing.xs
                        visible: Boolean(root.idea && root.idea.sourceLink && root.idea.sourceLink.length > 0)

                        Text {
                            text: i18nBridge.tr("label_source_url", "Kaynak URL")
                            font.pixelSize: Theme.typography.sizeSmall
                            font.weight: Theme.typography.weightSemiBold
                            color: themeBridge.color("text_secondary")
                        }

                        Text {
                            text: root.idea.sourceLink || ""
                            font.pixelSize: Theme.typography.sizeBody
                            color: Theme.accent(themeBridge.currentTheme)
                            wrapMode: Text.Wrap
                            Layout.fillWidth: true
                        }
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: themeBridge.color("border")
            }

            // Alt Eylem Butonları
            RowLayout {
                Layout.fillWidth: true
                spacing: Theme.spacing.md

                AppButton {
                    text: i18nBridge.tr("action_delete", "Sil")
                    btnVariant: "danger"
                    onClicked: {
                        if (ideaViewModel && root.hasIdea) {
                            ideaViewModel.deleteIdea(root.idea.id)
                        }
                    }
                }

                Item { Layout.fillWidth: true }

                AppButton {
                    text: i18nBridge.tr("action_edit", "Düzenle")
                    iconName: "pencil"
                    btnVariant: "secondary"
                    onClicked: {
                        if (ideaViewModel && root.hasIdea) {
                            ideaViewModel.openEditDialog(root.idea.id)
                        }
                    }
                }

                AppButton {
                    text: i18nBridge.tr("ideas_convert_btn", "Projeye Dönüştür")
                    iconName: "plus"
                    btnVariant: "primary"
                    visible: Boolean(root.hasIdea && root.idea && root.idea.status !== "CONVERTED")
                    onClicked: {
                        if (ideaViewModel && root.hasIdea) {
                            ideaViewModel.convertToProject(root.idea.id)
                        }
                    }
                }
            }
        }
    }
}
