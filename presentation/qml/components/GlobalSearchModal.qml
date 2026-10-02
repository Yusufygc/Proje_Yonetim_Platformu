import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: searchModalRoot
    anchors.fill: parent
    color: Qt.rgba(0, 0, 0, 0.65)
    visible: navBridge.searchModalOpen
    z: 9999

    MouseArea {
        anchors.fill: parent
        onClicked: navBridge.closeSearch()
    }

    Rectangle {
        id: dialogCard
        width: Math.min(620, parent.width - 48)
        height: 380
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: 80
        radius: 12
        color: themeBridge.surface
        border.width: 1
        border.color: themeBridge.accentStart

        MouseArea {
            anchors.fill: parent
            // Tıklamanın arkadaki karartma katmanına geçmesini engelle
        }

        Column {
            anchors.fill: parent
            anchors.margins: 16
            spacing: 12

            // Üst Arama Girdisi
            Rectangle {
                width: parent.width
                height: 44
                radius: 8
                color: themeBridge.background
                border.width: 1
                border.color: searchInput.activeFocus ? themeBridge.accentStart : themeBridge.border

                Row {
                    anchors.fill: parent
                    anchors.leftMargin: 12
                    anchors.rightMargin: 12
                    spacing: 8

                    AppIcon {
                        name: "search"
                        size: 18
                        color: themeBridge.textMuted
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    TextInput {
                        id: searchInput
                        width: parent.width - 60
                        anchors.verticalCenter: parent.verticalCenter
                        font.pixelSize: 14
                        color: themeBridge.textPrimary
                        selectByMouse: true

                        Text {
                            anchors.fill: parent
                            text: i18nBridge.tr("search_placeholder", "Proje, görev, fikir veya not ara...")
                            color: themeBridge.textMuted
                            font.pixelSize: 14
                            visible: !searchInput.text && !searchInput.activeFocus
                        }

                        Keys.onEscapePressed: navBridge.closeSearch()
                    }

                    Text {
                        text: "ESC"
                        font.pixelSize: 11
                        font.weight: Font.DemiBold
                        color: themeBridge.textMuted
                        anchors.verticalCenter: parent.verticalCenter
                    }
                }
            }

            // Ayraç
            Rectangle {
                width: parent.width
                height: 1
                color: themeBridge.border
            }

            // Arama İpucu / Sonuç Alanı
            Item {
                width: parent.width
                height: parent.height - 80

                Column {
                    anchors.centerIn: parent
                    spacing: 8
                    visible: !searchInput.text

                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: "🔍"
                        font.pixelSize: 28
                    }

                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: i18nBridge.tr("search_hint", "Aramak istediğiniz terimi yazın...")
                        font.pixelSize: 13
                        color: themeBridge.textMuted
                    }
                }
            }
        }
    }

    onVisibleChanged: {
        if (visible) {
            searchInput.text = "";
            searchInput.forceActiveFocus();
        }
    }
}
