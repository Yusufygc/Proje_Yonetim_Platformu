import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"

Item {
    id: projectsViewRoot
    anchors.fill: parent

    Column {
        anchors.fill: parent
        padding: 24
        spacing: 16

        // Üst Filtre ve Aksiyon Çubuğu
        Row {
            width: parent.width - 48
            spacing: 12

            Rectangle {
                width: 260
                height: 36
                radius: 8
                color: themeBridge.surface
                border.width: 1
                border.color: themeBridge.border

                Row {
                    anchors.fill: parent
                    anchors.leftMargin: 10
                    spacing: 8

                    AppIcon {
                        name: "search"
                        size: 16
                        color: themeBridge.textMuted
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    TextInput {
                        id: projectSearchInput
                        width: parent.width - 40
                        anchors.verticalCenter: parent.verticalCenter
                        font.pixelSize: 13
                        color: themeBridge.textPrimary
                        selectByMouse: true

                        Text {
                            anchors.fill: parent
                            text: i18nBridge.tr("project_search_placeholder", "Projelerde ara...")
                            color: themeBridge.textMuted
                            font.pixelSize: 13
                            visible: !projectSearchInput.text
                        }
                    }
                }
            }

            Item { width: 1; height: 1; Layout.fillWidth: true }

            AppButton {
                variant: "primary"
                text: i18nBridge.tr("btn_new_project", "Yeni Proje")
                iconName: "folder"
                onClicked: navBridge.createNewProject()
            }
        }

        // Proje Listesi ve Detay Alanı (Placeholder for Phase 2)
        AppCard {
            width: parent.width - 48
            height: parent.height - 100

            Column {
                anchors.centerIn: parent
                spacing: 12

                AppIcon {
                    name: "folder"
                    size: 48
                    color: themeBridge.accentStart
                    anchors.horizontalCenter: parent.horizontalCenter
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: i18nBridge.tr("projects_empty_title", "Projeler Yükleniyor...")
                    font.pixelSize: 16
                    font.weight: Font.DemiBold
                    color: themeBridge.textPrimary
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: i18nBridge.tr("projects_empty_desc", "Adım 2'de ProjectListModel ve Detay Paneli buraya bağlanacaktır.")
                    font.pixelSize: 13
                    color: themeBridge.textSecondary
                }
            }
        }
    }
}
