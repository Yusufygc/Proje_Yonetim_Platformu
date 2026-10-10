import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"

Rectangle {
    id: sidebarRoot

    readonly property bool isCollapsed: navBridge.sidebarCollapsed
    readonly property int expandedWidth: 240
    readonly property int collapsedWidth: 64
    readonly property bool isRoseTheme: themeBridge.isRose
    readonly property bool isOceanTheme: themeBridge.isOcean
    readonly property bool hasPatternTheme: isRoseTheme || isOceanTheme

    // Tema paketi arka plan deseni görsel kaynağı
    readonly property string patternImageSource: {
        if (isRoseTheme) return Qt.resolvedUrl("../../../resources/images/rose_sidebar.jpg");
        if (isOceanTheme) return Qt.resolvedUrl("../../../resources/images/ocean_sidebar.jpg");
        return "";
    }

    // Desenli temalarda yüksek kontrastlı metin rengi
    readonly property color patternTextColor: isRoseTheme ? "#FFF0F3" : "#F0F9FF"

    // Desenli temalarda karartma katmanı rengi
    readonly property color patternOverlayColor: {
        if (isRoseTheme) {
            return themeBridge.isDark ? Qt.rgba(0.08, 0.02, 0.05, 0.55) : Qt.rgba(0.18, 0.03, 0.10, 0.48);
        }
        if (isOceanTheme) {
            return themeBridge.isDark ? Qt.rgba(0.03, 0.08, 0.14, 0.52) : Qt.rgba(0.03, 0.12, 0.22, 0.46);
        }
        return "transparent";
    }

    width: isCollapsed ? collapsedWidth : expandedWidth
    color: themeBridge.sidebarBg
    clip: true

    Behavior on width {
        NumberAnimation {
            duration: 250
            easing.type: Easing.InOutCubic
        }
    }

    // Desenli Tema Arka Plan Görseli (Rose, Ocean)
    Image {
        id: patternBgImage
        anchors.fill: parent
        source: sidebarRoot.patternImageSource
        fillMode: Image.PreserveAspectCrop
        visible: sidebarRoot.hasPatternTheme
        opacity: sidebarRoot.isCollapsed ? 0.32 : 0.40
        clip: true
        asynchronous: true
        smooth: true

        Behavior on opacity { NumberAnimation { duration: 200 } }
    }

    // Desenli Tema Okunabilirlik ve Şeffaflık Karartma Katmanı
    Rectangle {
        id: patternOverlay
        anchors.fill: parent
        visible: sidebarRoot.hasPatternTheme
        color: sidebarRoot.patternOverlayColor
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
                    color: toggleMouse.containsMouse ? themeBridge.sidebarTextActive : (sidebarRoot.hasPatternTheme ? sidebarRoot.patternTextColor : themeBridge.sidebarText)
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
            color: searchMouse.containsMouse ? Qt.rgba(1, 1, 1, 0.22) : (sidebarRoot.hasPatternTheme ? Qt.rgba(0, 0, 0, 0.28) : Qt.rgba(1, 1, 1, 0.12))
            border.width: 1
            border.color: sidebarRoot.hasPatternTheme ? Qt.rgba(1, 1, 1, 0.22) : Qt.rgba(1, 1, 1, 0.2)
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
                    if (sidebarRoot.hasPatternTheme) return Qt.rgba(0, 0, 0, 0.22);
                    return "transparent";
                }

                border.width: isActive ? 1 : (sidebarRoot.hasPatternTheme ? 1 : 0)
                border.color: isActive ? themeBridge.sidebarActive : (sidebarRoot.hasPatternTheme ? Qt.rgba(1, 1, 1, 0.08) : "transparent")

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
                                return sidebarRoot.hasPatternTheme ? sidebarRoot.patternTextColor : themeBridge.sidebarText;
                            }
                            anchors.centerIn: parent
                        }
                    }

                    Text {
                        text: i18nBridge.tr(modelData.label_key, modelData.default_label)
                        font.pixelSize: 13
                        font.weight: navItem.isActive ? Font.DemiBold : (sidebarRoot.hasPatternTheme ? Font.Medium : Font.Normal)
                        color: {
                            if (navItem.isActive) return themeBridge.sidebarTextActive;
                            if (navItem.isHovered) return themeBridge.sidebarTextActive;
                            return sidebarRoot.hasPatternTheme ? sidebarRoot.patternTextColor : themeBridge.sidebarText;
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
                    color: sidebarRoot.hasPatternTheme ? sidebarRoot.patternTextColor : themeBridge.sidebarText
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
            color: sidebarRoot.hasPatternTheme ? Qt.rgba(1, 1, 1, 0.65) : themeBridge.textMuted
            horizontalAlignment: Text.AlignHCenter
            visible: !sidebarRoot.isCollapsed
        }
    }
}
