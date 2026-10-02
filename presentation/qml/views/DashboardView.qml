import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"

ScrollView {
    id: viewRoot
    anchors.fill: parent
    contentWidth: availableWidth
    clip: true

    Column {
        width: parent.width
        padding: 24
        spacing: 20

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
                        text: "--"
                        font.pixelSize: 26
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
                            text: i18nBridge.tr("dash_pending_tasks", "Bekleyen Görevler")
                            font.pixelSize: 13
                            color: themeBridge.textSecondary
                            width: parent.width - 24
                        }
                        AppIcon { name: "square-check"; size: 18; color: themeBridge.warning }
                    }

                    Text {
                        text: "--"
                        font.pixelSize: 26
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
                            text: i18nBridge.tr("dash_completed_tasks", "Tamamlanan")
                            font.pixelSize: 13
                            color: themeBridge.textSecondary
                            width: parent.width - 24
                        }
                        AppIcon { name: "check_square"; size: 18; color: themeBridge.success }
                    }

                    Text {
                        text: "--"
                        font.pixelSize: 26
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
                        text: "--"
                        font.pixelSize: 26
                        font.bold: true
                        color: themeBridge.textPrimary
                    }
                }
            }
        }

        // Hızlı Başlangıç Paneli
        AppCard {
            width: parent.width - 48
            height: 180

            Column {
                anchors.fill: parent
                spacing: 12

                Text {
                    text: i18nBridge.tr("dash_welcome_title", "Hoş Geldiniz!")
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
    }
}
