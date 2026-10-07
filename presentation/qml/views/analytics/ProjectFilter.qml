import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../components"

// Proje seçimi: açılır menü; seçim analyticsViewModel.projectId'ye yazılır.
    Rectangle {
        id: projSelectBox
        width: 240
        height: 36
        radius: 8
        color: themeBridge.surface
        border.width: 1
        border.color: projMouse.containsMouse || projMenu.opened ? themeBridge.accentStart : themeBridge.border

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 12
            anchors.rightMargin: 12
            spacing: 8

            AppIcon {
                name: analyticsViewModel.projectId === 0 ? "dashboard" : "folder"
                size: 14
                color: themeBridge.accentStart
                Layout.alignment: Qt.AlignVCenter
            }

            Text {
                Layout.fillWidth: true
                text: {
                    var pList = analyticsViewModel.projects;
                    for (var i = 0; i < pList.length; i++) {
                        if (pList[i].id === analyticsViewModel.projectId) {
                            return pList[i].title;
                        }
                    }
                    return i18nBridge.tr("analytics_all_projects", "Tüm Projeler");
                }
                font.pixelSize: 12
                font.weight: Font.Medium
                color: themeBridge.textPrimary
                elide: Text.ElideRight
                Layout.alignment: Qt.AlignVCenter
            }

            Text {
                text: projMenu.opened ? "▲" : "▼"
                font.pixelSize: 9
                color: themeBridge.textMuted
                Layout.alignment: Qt.AlignVCenter
            }
        }

        MouseArea {
            id: projMouse
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: {
                if (projMenu.opened) {
                    projMenu.close();
                } else {
                    projMenu.open();
                }
            }
        }

        Menu {
            id: projMenu
            y: projSelectBox.height + 4
            width: Math.max(projSelectBox.width, 280)
            padding: 6

            background: Rectangle {
                radius: 8
                color: themeBridge.surface
                border.width: 1
                border.color: themeBridge.border
            }

            Repeater {
                model: analyticsViewModel.projects
                MenuItem {
                    id: projItem
                    height: 36
                    padding: 0

                    contentItem: RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 10
                        anchors.rightMargin: 10
                        spacing: 8

                        AppIcon {
                            name: modelData.id === 0 ? "dashboard" : "folder"
                            size: 14
                            color: analyticsViewModel.projectId === modelData.id ?
                                   themeBridge.accentStart :
                                   (projItem.hovered ? themeBridge.textPrimary : themeBridge.textMuted)
                            Layout.alignment: Qt.AlignVCenter
                        }

                        Text {
                            Layout.fillWidth: true
                            text: modelData.title
                            font.pixelSize: 12
                            font.weight: analyticsViewModel.projectId === modelData.id ? Font.DemiBold : Font.Normal
                            color: analyticsViewModel.projectId === modelData.id ?
                                   themeBridge.accentStart :
                                   (projItem.hovered ? themeBridge.textPrimary : themeBridge.textSecondary)
                            elide: Text.ElideRight
                            verticalAlignment: Text.AlignVCenter
                            Layout.alignment: Qt.AlignVCenter
                        }

                        Text {
                            text: "✓"
                            font.pixelSize: 12
                            font.bold: true
                            color: themeBridge.accentStart
                            visible: analyticsViewModel.projectId === modelData.id
                            Layout.alignment: Qt.AlignVCenter
                        }
                    }

                    background: Rectangle {
                        radius: 6
                        color: {
                            if (analyticsViewModel.projectId === modelData.id) {
                                return themeBridge.isDark ? Qt.rgba(0.39, 0.4, 0.95, 0.16) : Qt.rgba(0.39, 0.4, 0.95, 0.08);
                            }
                            if (projItem.hovered) {
                                return themeBridge.isDark ? themeBridge.surfaceRaised : "#F1F5F9";
                            }
                            return "transparent";
                        }
                    }

                    onTriggered: analyticsViewModel.setProjectId(modelData.id)
                }
            }
        }
    }
