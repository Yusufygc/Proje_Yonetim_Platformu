import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"

Rectangle {
    id: searchModalRoot
    anchors.fill: parent
    color: Qt.rgba(0, 0, 0, 0.65)
    visible: navBridge.searchModalOpen
    z: 9999

    MouseArea {
        anchors.fill: parent
        onClicked: {
            searchViewModel.clear();
            navBridge.closeSearch();
        }
    }

    Shortcut {
        sequence: "Escape"
        enabled: searchModalRoot.visible
        onActivated: {
            searchViewModel.clear();
            navBridge.closeSearch();
        }
    }

    Rectangle {
        id: dialogCard
        width: Math.min(640, parent.width - 48)
        height: 420
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
                        width: parent.width - 70
                        anchors.verticalCenter: parent.verticalCenter
                        font.pixelSize: 14
                        color: themeBridge.textPrimary
                        selectByMouse: true

                        Text {
                            anchors.fill: parent
                            text: i18nBridge.tr("search_placeholder", "Proje, görev veya fikir ara...")
                            color: themeBridge.textMuted
                            font.pixelSize: 14
                            visible: !searchInput.text && !searchInput.activeFocus
                        }

                        onTextChanged: searchViewModel.search(text)

                        Keys.onEscapePressed: {
                            searchViewModel.clear();
                            navBridge.closeSearch();
                        }

                        Keys.onReturnPressed: {
                            if (searchViewModel.count > 0) {
                                var first = searchViewModel.results[0];
                                searchViewModel.selectItem(first.type, first.id);
                            }
                        }
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
                height: parent.height - 76

                // 1. Yazı Yokken İpucu
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
                        text: i18nBridge.tr("search_hint", "Projelerde, görevlerde ve fikirlerde arama yapın...")
                        font.pixelSize: 13
                        color: themeBridge.textMuted
                    }
                }

                // 2. Sonuç Bulunamadı
                Column {
                    anchors.centerIn: parent
                    spacing: 8
                    visible: searchInput.text.length >= 2 && searchViewModel.count === 0 && !searchViewModel.isSearching

                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: i18nBridge.tr("search_not_found", "Eşleşen sonuç bulunamadı.")
                        font.pixelSize: 14
                        font.weight: Font.DemiBold
                        color: themeBridge.textSecondary
                    }
                }

                // 3. Sonuç Listesi
                ScrollView {
                    anchors.fill: parent
                    contentWidth: availableWidth
                    clip: true
                    visible: searchViewModel.count > 0

                    Column {
                        width: parent.width
                        spacing: 6

                        Repeater {
                            model: searchViewModel.results

                            Rectangle {
                                width: parent.width
                                height: 54
                                radius: 8
                                color: resMouse.containsMouse ? themeBridge.surfaceHover : "transparent"

                                Row {
                                    anchors.fill: parent
                                    anchors.leftMargin: 10
                                    anchors.rightMargin: 10
                                    spacing: 12

                                    // Tür İkonu
                                    Rectangle {
                                        width: 32
                                        height: 32
                                        radius: 6
                                        color: Qt.rgba(0.2, 0.4, 0.8, 0.1)
                                        anchors.verticalCenter: parent.verticalCenter

                                        AppIcon {
                                            name: modelData.icon
                                            size: 16
                                            color: modelData.color
                                            anchors.centerIn: parent
                                        }
                                    }

                                    // Başlık ve Açıklama
                                    Column {
                                        width: parent.width - 120
                                        anchors.verticalCenter: parent.verticalCenter
                                        spacing: 2

                                        Row {
                                            spacing: 6
                                            AppBadge {
                                                text: modelData.typeLabel
                                                variant: "neutral"
                                            }

                                            Text {
                                                text: modelData.title
                                                font.pixelSize: 13
                                                font.weight: Font.DemiBold
                                                color: themeBridge.textPrimary
                                                elide: Text.ElideRight
                                                maximumLineCount: 1
                                            }
                                        }

                                        Text {
                                            text: modelData.description || i18nBridge.tr("common_no_desc", "Açıklama yok")
                                            font.pixelSize: 11
                                            color: themeBridge.textSecondary
                                            elide: Text.ElideRight
                                            maximumLineCount: 1
                                            width: parent.width
                                        }
                                    }

                                    Text {
                                        text: "↵"
                                        font.pixelSize: 14
                                        color: themeBridge.textMuted
                                        anchors.verticalCenter: parent.verticalCenter
                                        visible: resMouse.containsMouse
                                    }
                                }

                                MouseArea {
                                    id: resMouse
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: searchViewModel.selectItem(modelData.type, modelData.id)
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    onVisibleChanged: {
        if (visible) {
            searchInput.text = "";
            searchViewModel.clear();
            searchInput.forceActiveFocus();
        }
    }
}
