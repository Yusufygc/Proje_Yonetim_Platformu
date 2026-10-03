import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"
import "projects"
import "../dialogs"

Item {
    id: projectsViewRoot
    anchors.fill: parent

    property string activeStatusFilter: "ALL"

    // Sol Liste Paneli (340px)
    Rectangle {
        id: leftPanel
        width: 340
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        color: themeBridge.surface
        border.width: 1
        border.color: themeBridge.border

        Column {
            anchors.fill: parent
            padding: 16
            spacing: 12

            // Üst Başlık ve Yeni Buton
            Row {
                width: parent.width - 32
                spacing: 8

                Text {
                    text: i18nBridge.tr("nav_projects", "Projeler")
                    font.pixelSize: 18
                    font.weight: Font.Bold
                    color: themeBridge.textPrimary
                    anchors.verticalCenter: parent.verticalCenter
                    width: parent.width - 40
                }

                AppButton {
                    variant: "primary"
                    iconName: "plus"
                    implicitWidth: 32
                    implicitHeight: 32
                    onClicked: projectViewModel.openCreateDialog()
                    anchors.verticalCenter: parent.verticalCenter
                }
            }

                // Arama Kutusu
                Rectangle {
                    width: parent.width - 32
                    height: 36
                    radius: 8
                    color: themeBridge.background
                    border.width: 1
                    border.color: searchInput.activeFocus ? themeBridge.accentStart : themeBridge.border

                    Row {
                        anchors.fill: parent
                        anchors.leftMargin: 10
                        anchors.rightMargin: 10
                        spacing: 8

                        AppIcon {
                            name: "search"
                            size: 16
                            color: themeBridge.textMuted
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        TextInput {
                            id: searchInput
                            width: parent.width - 30
                            anchors.verticalCenter: parent.verticalCenter
                            font.pixelSize: 13
                            color: themeBridge.textPrimary
                            selectByMouse: true
                            onTextChanged: projectViewModel.model.setSearchQuery(text)

                            Text {
                                anchors.fill: parent
                                text: i18nBridge.tr("project_search_placeholder", "Projelerde ara...")
                                color: themeBridge.textMuted
                                font.pixelSize: 13
                                visible: !searchInput.text && !searchInput.activeFocus
                            }
                        }
                    }
                }

                // Durum Filtreleme Butonları (Pills)
                ScrollView {
                    width: parent.width - 32
                    height: 32
                    contentWidth: filterRow.implicitWidth
                    ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                    ScrollBar.vertical.policy: ScrollBar.AlwaysOff
                    clip: true

                    Row {
                        id: filterRow
                        spacing: 4

                        Repeater {
                            model: [
                                {"key": "ALL", "label": i18nBridge.tr("filter_all", "Tümü")},
                                {"key": "ACTIVE", "label": i18nBridge.tr("status_active", "Aktif")},
                                {"key": "PLANNED", "label": i18nBridge.tr("status_planned", "Planlanan")},
                                {"key": "COMPLETED", "label": i18nBridge.tr("status_completed", "Biten")},
                                {"key": "ON_HOLD", "label": i18nBridge.tr("status_on_hold", "Bekleyen")}
                            ]

                            Rectangle {
                                width: filterText.implicitWidth + 14
                                height: 26
                                radius: 13
                                color: projectsViewRoot.activeStatusFilter === modelData.key ? themeBridge.accentStart : themeBridge.background
                                border.width: 1
                                border.color: projectsViewRoot.activeStatusFilter === modelData.key ? themeBridge.accentStart : themeBridge.border

                                Text {
                                    id: filterText
                                    anchors.centerIn: parent
                                    text: modelData.label
                                    font.pixelSize: 11
                                    font.weight: Font.Medium
                                    color: projectsViewRoot.activeStatusFilter === modelData.key ? themeBridge.iconOnAccent : themeBridge.textSecondary
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: {
                                        projectsViewRoot.activeStatusFilter = modelData.key;
                                        projectViewModel.model.setStatusFilter(modelData.key);
                                    }
                                }
                            }
                        }
                    }
                }

                // Proje Listesi
                ListView {
                    id: projectList
                    width: parent.width - 32
                    height: parent.height - 140
                    model: projectViewModel.model
                    clip: true
                    spacing: 8

                    delegate: ProjectListItem {
                        projectId: model.projectId
                        title: model.title
                        projectType: model.projectType
                        status: model.status
                        priority: model.priority
                        progress: model.progress
                        isSelected: projectViewModel.selectedProjectId === model.projectId
                        onClicked: projectViewModel.selectProject(model.projectId)
                    }

                    // Boş Liste Durumu
                    Text {
                        anchors.centerIn: parent
                        text: i18nBridge.tr("projects_empty", "Henüz proje bulunmuyor.")
                        font.pixelSize: 13
                        color: themeBridge.textMuted
                        visible: projectList.count === 0
                    }
                }
            }
        }

        // Sağ Detay Paneli
        ProjectDetailPanel {
            anchors.left: leftPanel.right
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
        }

    // Proje Ekle/Düzenle Dialogu
    ProjectDialog {
        anchors.fill: parent
    }
}
