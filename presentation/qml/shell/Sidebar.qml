import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"

Rectangle {
    id: sidebarRoot

    readonly property bool isCollapsed: navBridge.sidebarCollapsed
    readonly property int expandedWidth: 240
    readonly property int collapsedWidth: 64

    width: isCollapsed ? collapsedWidth : expandedWidth
    color: themeBridge.sidebarBg

    Behavior on width {
        NumberAnimation {
            duration: 250
            easing.type: Easing.InOutCubic
        }
    }

    Column {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 8

        // Header: Başlık ve Daraltma/Genişletme Butonu
        Item {
            width: parent.width
            height: 38

            Text {
                id: titleLabel
                text: i18nBridge.tr("app_short_name", "Proje Takip")
                font.pixelSize: 16
                font.weight: Font.Bold
                color: themeBridge.sidebarTextActive
                anchors.left: parent.left
                anchors.leftMargin: 8
                anchors.verticalCenter: parent.verticalCenter
                visible: !sidebarRoot.isCollapsed
                opacity: sidebarRoot.isCollapsed ? 0.0 : 1.0
                Behavior on opacity { NumberAnimation { duration: 150 } }
            }

            Rectangle {
                id: toggleBtn
                width: 32
                height: 32
                radius: 6
                anchors.right: sidebarRoot.isCollapsed ? undefined : parent.right
                anchors.horizontalCenter: sidebarRoot.isCollapsed ? parent.horizontalCenter : undefined
                anchors.verticalCenter: parent.verticalCenter
                color: toggleMouse.containsMouse ? themeBridge.sidebarHoverBg : "transparent"

                AppIcon {
                    name: "menu"
                    size: 18
                    color: toggleMouse.containsMouse ? themeBridge.sidebarTextActive : themeBridge.sidebarText
                    anchors.centerIn: parent
                }

                MouseArea {
                    id: toggleMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: navBridge.toggleSidebar()
                }
            }
        }

        // Hızlı Arama Butonu
        Rectangle {
            id: searchBtn
            width: sidebarRoot.isCollapsed ? 36 : parent.width
            height: 36
            radius: 8
            anchors.horizontalCenter: sidebarRoot.isCollapsed ? parent.horizontalCenter : undefined
            color: searchMouse.containsMouse ? Qt.rgba(1, 1, 1, 0.22) : Qt.rgba(1, 1, 1, 0.12)
            border.width: 1
            border.color: Qt.rgba(1, 1, 1, 0.2)
            // Kenar çubuğu daralırken genişlik animasyonlu değişir; taşan yazı kutunun dışına çıkmasın.
            clip: true

            Row {
                anchors.centerIn: parent
                spacing: 8

                AppIcon {
                    name: "search"
                    size: 16
                    color: "#FFFFFF"
                    anchors.verticalCenter: parent.verticalCenter
                }

                Text {
                    text: i18nBridge.tr("sidebar_search", "Ara (Ctrl+F)")
                    font.pixelSize: 12
                    color: "#FFFFFF"
                    opacity: 0.85
                    // Simge (16) + boşluk (8) + iç kenar payı (24) düşülür; sığmayan yazı kısaltılır.
                    width: Math.min(implicitWidth, Math.max(0, searchBtn.width - 48))
                    elide: Text.ElideRight
                    visible: !sidebarRoot.isCollapsed && width > 24
                    anchors.verticalCenter: parent.verticalCenter
                }
            }

            MouseArea {
                id: searchMouse
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: navBridge.openSearch()
            }
        }

        // Ayraç Çizgisi
        Rectangle {
            width: parent.width
            height: 1
            color: Qt.rgba(1, 1, 1, 0.12)
        }

        // Modül Navigasyon Butonları Listesi
        ListView {
            id: navList
            width: parent.width
            height: parent.height - 180
            model: navBridge.modules
            clip: true
            spacing: 4

            delegate: Rectangle {
                id: navItem
                width: navList.width
                height: 42
                radius: 8

                readonly property bool isActive: navBridge.currentPage === modelData.page_key
                readonly property bool isHovered: itemMouse.containsMouse

                color: {
                    if (isActive) return themeBridge.sidebarActiveBg;
                    if (isHovered) return themeBridge.sidebarHoverBg;
                    return "transparent";
                }

                border.width: isActive ? 1 : 0
                border.color: isActive ? themeBridge.sidebarActive : "transparent"

                Behavior on color { ColorAnimation { duration: 120 } }

                Row {
                    anchors.fill: parent
                    anchors.leftMargin: sidebarRoot.isCollapsed ? 0 : 12
                    spacing: 12

                    Item {
                        width: sidebarRoot.isCollapsed ? navItem.width : 20
                        height: parent.height

                        AppIcon {
                            name: modelData.icon
                            size: 18
                            color: {
                                if (navItem.isActive) return themeBridge.iconOnAccent;
                                if (navItem.isHovered) return themeBridge.sidebarTextActive;
                                return themeBridge.sidebarText;
                            }
                            anchors.centerIn: parent
                        }
                    }

                    Text {
                        text: i18nBridge.tr(modelData.label_key, modelData.default_label)
                        font.pixelSize: 13
                        font.weight: navItem.isActive ? Font.Medium : Font.Normal
                        color: {
                            if (navItem.isActive) return themeBridge.sidebarTextActive;
                            if (navItem.isHovered) return themeBridge.sidebarTextActive;
                            return themeBridge.sidebarText;
                        }
                        anchors.verticalCenter: parent.verticalCenter
                        visible: !sidebarRoot.isCollapsed
                    }
                }

                MouseArea {
                    id: itemMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: navBridge.navigateTo(modelData.page_key)
                }

                // Daraltılmış modda ToolTip
                ToolTip.visible: sidebarRoot.isCollapsed && isHovered
                ToolTip.text: i18nBridge.tr(modelData.label_key, modelData.default_label)
                ToolTip.delay: 300
            }
        }

        // Alt Kısım: Tema Değiştirme ve Sürüm
        Item {
            width: parent.width
            height: 44

            // Geniş modda tema satırı
            Row {
                anchors.fill: parent
                visible: !sidebarRoot.isCollapsed
                spacing: 8

                Text {
                    text: themeBridge.isDark ? i18nBridge.tr("theme_dark", "Koyu Tema") : i18nBridge.tr("theme_light", "Açık Tema")
                    font.pixelSize: 12
                    color: themeBridge.sidebarText
                    anchors.verticalCenter: parent.verticalCenter
                    width: parent.width - 50
                    elide: Text.ElideRight
                }

                // Switch
                Rectangle {
                    width: 44
                    height: 24
                    radius: 12
                    color: themeBridge.isDark ? themeBridge.surfaceRaised : themeBridge.accentStart
                    anchors.verticalCenter: parent.verticalCenter

                    Rectangle {
                        width: 18
                        height: 18
                        radius: 9
                        color: "#FFFFFF"
                        x: themeBridge.isDark ? 3 : 23
                        anchors.verticalCenter: parent.verticalCenter
                        Behavior on x { NumberAnimation { duration: 150 } }
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: themeBridge.toggleTheme()
                    }
                }
            }

            // Dar modda tek ikon butonu
            Rectangle {
                width: 36
                height: 36
                radius: 18
                color: themeMouse.containsMouse ? Qt.rgba(1, 1, 1, 0.25) : Qt.rgba(1, 1, 1, 0.14)
                border.width: 1
                border.color: Qt.rgba(1, 1, 1, 0.2)
                anchors.centerIn: parent
                visible: sidebarRoot.isCollapsed

                AppIcon {
                    name: themeBridge.isDark ? "moon" : "sun"
                    size: 16
                    color: "#FFFFFF"
                    anchors.centerIn: parent
                }

                MouseArea {
                    id: themeMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: themeBridge.toggleTheme()
                }

                ToolTip.visible: sidebarRoot.isCollapsed && themeMouse.containsMouse
                ToolTip.text: themeBridge.isDark ? i18nBridge.tr("theme_dark", "Koyu Tema") : i18nBridge.tr("theme_light", "Açık Tema")
                ToolTip.delay: 300
            }
        }

        // Sürüm etiketi
        Text {
            width: parent.width
            text: "v" + settingsViewModel.appVersion
            font.pixelSize: 11
            color: themeBridge.textMuted
            horizontalAlignment: Text.AlignHCenter
            visible: !sidebarRoot.isCollapsed
        }
    }
}
