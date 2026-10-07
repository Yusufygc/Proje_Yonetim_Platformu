import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"

ScrollView {
    id: viewRoot
    anchors.fill: parent
    contentWidth: availableWidth
    clip: true

    ScrollBar.vertical: AppScrollBar { }

    Column {
        width: parent.width
        padding: 24
        spacing: 20

        // ── Sayfa Başlığı ────────────────────────────────────────────────────
        Row {
            width: parent.width - 48
            spacing: 12

            Column {
                spacing: 4
                Text {
                    text: i18nBridge.tr("nav_dashboard", "Ana Panel")
                    font.pixelSize: 22
                    font.weight: Font.Bold
                    color: themeBridge.textPrimary
                }
                Text {
                    text: i18nBridge.tr("dash_welcome_desc", "Projelerinizi, görevlerinizi ve fikirlerinizi merkezi olarak yönetmeye başlayın.")
                    font.pixelSize: 13
                    color: themeBridge.textSecondary
                }
            }
        }

        // Üst İstatistik Kartları Izgarası (Grid)
        Grid {
            width: parent.width - 48
            columns: Math.max(1, Math.min(4, Math.floor(width / 240)))
            spacing: 16

            AppCard {
                width: (parent.width - (parent.columns - 1) * parent.spacing) / parent.columns
                height: 110
                hoverable: true

                Column {
                    anchors.fill: parent
                    spacing: 8

                    Row {
                        width: parent.width
                        Text {
                            text: i18nBridge.tr("dash_active_projects", "Aktif Projeler")
                            font.pixelSize: 13
                            color: themeBridge.textSecondary
                            width: parent.width - 24
                        }
                        AppIcon { name: "folder"; size: 18; color: themeBridge.accentStart }
                    }

                    Text {
                        text: dashboardViewModel.activeProjects.toString()
                        font.pixelSize: 28
                        font.bold: true
                        color: themeBridge.textPrimary
                    }
                }
            }

            AppCard {
                width: (parent.width - (parent.columns - 1) * parent.spacing) / parent.columns
                height: 110
                hoverable: true

                Column {
                    anchors.fill: parent
                    spacing: 8

                    Row {
                        width: parent.width
                        Text {
                            text: i18nBridge.tr("dash_pending_tasks", "Açık Görevler")
                            font.pixelSize: 13
                            color: themeBridge.textSecondary
                            width: parent.width - 24
                        }
                        AppIcon { name: "square-check"; size: 18; color: themeBridge.warning }
                    }

                    Text {
                        text: dashboardViewModel.openTasks.toString()
                        font.pixelSize: 28
                        font.bold: true
                        color: themeBridge.textPrimary
                    }
                }
            }

            AppCard {
                width: (parent.width - (parent.columns - 1) * parent.spacing) / parent.columns
                height: 110
                hoverable: true

                Column {
                    anchors.fill: parent
                    spacing: 8

                    Row {
                        width: parent.width
                        Text {
                            text: i18nBridge.tr("dash_completed_tasks", "Tamamlanan Görevler")
                            font.pixelSize: 13
                            color: themeBridge.textSecondary
                            width: parent.width - 24
                        }
                        AppIcon { name: "check_square"; size: 18; color: themeBridge.success }
                    }

                    Text {
                        text: dashboardViewModel.completedTasks.toString()
                        font.pixelSize: 28
                        font.bold: true
                        color: themeBridge.textPrimary
                    }
                }
            }

            AppCard {
                width: (parent.width - (parent.columns - 1) * parent.spacing) / parent.columns
                height: 110
                hoverable: true

                Column {
                    anchors.fill: parent
                    spacing: 8

                    Row {
                        width: parent.width
                        Text {
                            text: i18nBridge.tr("dash_ideas", "Havuzdaki Fikirler")
                            font.pixelSize: 13
                            color: themeBridge.textSecondary
                            width: parent.width - 24
                        }
                        AppIcon { name: "lightbulb"; size: 18; color: themeBridge.accentStart }
                    }

                    Text {
                        text: dashboardViewModel.totalIdeas.toString()
                        font.pixelSize: 28
                        font.bold: true
                        color: themeBridge.textPrimary
                    }
                }
            }
        }

        // Hızlı Başlangıç & Aksiyonlar Paneli
        AppCard {
            width: parent.width - 48
            height: 140

            Column {
                anchors.fill: parent
                spacing: 12

                Text {
                    text: i18nBridge.tr("dash_welcome_title", "Proje Takip Merkezi")
                    font.pixelSize: 16
                    font.weight: Font.DemiBold
                    color: themeBridge.textPrimary
                }

                Text {
                    text: i18nBridge.tr("dash_welcome_desc", "Projelerinizi, görevlerinizi ve fikirlerinizi merkezi olarak yönetmeye başlayın.")
                    font.pixelSize: 13
                    color: themeBridge.textSecondary
                    wrapMode: Text.WordWrap
                    width: parent.width
                }

                Row {
                    spacing: 12
                    AppButton {
                        variant: "primary"
                        text: i18nBridge.tr("btn_new_project", "Yeni Proje")
                        iconName: "folder"
                        onClicked: navBridge.createNewProject()
                    }
                    AppButton {
                        variant: "secondary"
                        text: i18nBridge.tr("nav_ideas", "Fikirler")
                        iconName: "lightbulb"
                        onClicked: navBridge.navigateTo("ideas")
                    }
                    AppButton {
                        variant: "secondary"
                        text: i18nBridge.tr("nav_tasks", "Görevler")
                        iconName: "square-check"
                        onClicked: navBridge.navigateTo("tasks")
                    }
                }
            }
        }

        // Öncelikli Görevler ve Son Aktiviteler
        Row {
            width: parent.width - 48
            spacing: 16

            AppCard {
                width: (parent.width - 16) / 2
                height: 240

                Column {
                    anchors.fill: parent
                    spacing: 12

                    Row {
                        width: parent.width
                        Text {
                            text: i18nBridge.tr("dashboard_high_priority_title", "Yüksek Öncelikli Açık Görevler")
                            font.pixelSize: 14
                            font.weight: Font.DemiBold
                            color: themeBridge.textPrimary
                            width: parent.width - 24
                        }
                        AppIcon { name: "square-check"; size: 16; color: themeBridge.danger }
                    }

                    Repeater {
                        model: dashboardViewModel.highPriorityTasks.slice(0, 4)
                        delegate: Row {
                            width: parent.width
                            height: 28
                            spacing: 8

                            StatusIndicator {
                                status: modelData.status || "PLANNED"
                                showLabel: false
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            Text {
                                text: modelData.title || ""
                                font.pixelSize: 12
                                color: themeBridge.textPrimary
                                width: parent.width - 90
                                elide: Text.ElideRight
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            AppProgressBar {
                                value: modelData.progress || 0
                                barHeight: 4
                                implicitWidth: 60
                                anchors.verticalCenter: parent.verticalCenter
                            }
                        }
                    }

                    Column {
                        visible: dashboardViewModel.highPriorityTasks.length === 0
                        width: parent.width
                        spacing: 8
                        topPadding: 36

                        AppIcon {
                            name: "check"
                            size: 28
                            color: themeBridge.textMuted
                            anchors.horizontalCenter: parent.horizontalCenter
                        }

                        Text {
                            text: i18nBridge.tr("dashboard_no_high_priority", "Kritik veya yüksek öncelikli görev bulunmuyor.")
                            font.pixelSize: 12
                            color: themeBridge.textMuted
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                    }
                }
            }

            AppCard {
                width: (parent.width - 16) / 2
                height: 240

                Column {
                    anchors.fill: parent
                    spacing: 12

                    Row {
                        width: parent.width
                        Text {
                            text: i18nBridge.tr("dashboard_recent_ideas_title", "Son Eklenen Fikirler")
                            font.pixelSize: 14
                            font.weight: Font.DemiBold
                            color: themeBridge.textPrimary
                            width: parent.width - 24
                        }
                        AppIcon { name: "lightbulb"; size: 16; color: themeBridge.accentStart }
                    }

                    Repeater {
                        model: dashboardViewModel.recentIdeas.slice(0, 4)
                        delegate: Row {
                            width: parent.width
                            height: 28
                            spacing: 8

                            Text {
                                text: "💡"
                                font.pixelSize: 12
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            Text {
                                text: modelData.title || ""
                                font.pixelSize: 12
                                color: themeBridge.textPrimary
                                width: parent.width - 90
                                elide: Text.ElideRight
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            Text {
                                text: modelData.created_at || ""
                                font.pixelSize: 11
                                color: themeBridge.textMuted
                                anchors.verticalCenter: parent.verticalCenter
                            }
                        }
                    }

                    Column {
                        visible: dashboardViewModel.recentIdeas.length === 0
                        width: parent.width
                        spacing: 8
                        topPadding: 36

                        AppIcon {
                            name: "lightbulb"
                            size: 28
                            color: themeBridge.textMuted
                            anchors.horizontalCenter: parent.horizontalCenter
                        }

                        Text {
                            text: i18nBridge.tr("dashboard_no_recent_ideas", "Henüz fikir eklenmedi.")
                            font.pixelSize: 12
                            color: themeBridge.textMuted
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                    }
                }
            }
        }
    }
}
