import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"

ScrollView {
    id: settingsViewRoot
    anchors.fill: parent
    contentWidth: availableWidth
    clip: true

    ScrollBar.vertical: AppScrollBar { }

    property string pendingFont: settingsViewModel.fontFamily

    Column {
        width: parent.width
        padding: 24
        spacing: 24

        // Başlık
        Column {
            spacing: 4
            Text {
                text: i18nBridge.tr("settings_title", "Uygulama Ayarları")
                font.pixelSize: 22
                font.weight: Font.Bold
                color: themeBridge.textPrimary
            }
            Text {
                text: i18nBridge.tr("settings_subtitle", "Görünüm, tema, yazı tipi, dil ve veri yönetimi tercihleri")
                font.pixelSize: 13
                color: themeBridge.textSecondary
            }
        }

        // ── 1. Görünüm ve Tema Bölümü ────────────────────────────────────────
        AppCard {
            width: parent.width - 48
            height: 180

            Column {
                anchors.fill: parent
                spacing: 16

                Text {
                    text: i18nBridge.tr("settings_theme_section", "Tema ve Görünüm")
                    font.pixelSize: 15
                    font.weight: Font.DemiBold
                    color: themeBridge.textPrimary
                }

                // Mod Seçimi: Koyu / Açık
                Row {
                    spacing: 12

                    Text {
                        text: i18nBridge.tr("settings_theme_active_mode", "Aktif Mod:")
                        font.pixelSize: 13
                        color: themeBridge.textSecondary
                        anchors.verticalCenter: parent.verticalCenter
                        width: 100
                    }

                    AppButton {
                        text: "🌙"
                        variant: settingsViewModel.isDark ? "primary" : "secondary"
                        onClicked: settingsViewModel.setMode(true)
                        ToolTip.visible: hovered
                        ToolTip.text: i18nBridge.tr("settings_theme_mode_dark", "Koyu Mod")
                        ToolTip.delay: 300
                    }

                    AppButton {
                        text: "☀️"
                        variant: !settingsViewModel.isDark ? "primary" : "secondary"
                        onClicked: settingsViewModel.setMode(false)
                        ToolTip.visible: hovered
                        ToolTip.text: i18nBridge.tr("settings_theme_mode_light", "Açık Mod")
                        ToolTip.delay: 300
                    }
                }

                // Tema Paketi Seçimi
                Row {
                    spacing: 12

                    Text {
                        text: i18nBridge.tr("settings_theme_package_label", "Tema Paketi:")
                        font.pixelSize: 13
                        color: themeBridge.textSecondary
                        anchors.verticalCenter: parent.verticalCenter
                        width: 100
                    }

                    Repeater {
                        model: settingsViewModel.themePackages

                        Rectangle {
                            width: 90
                            height: 34
                            radius: 6
                            color: settingsViewModel.activePackage === modelData.id ? themeBridge.surfaceRaised : "transparent"
                            border.width: settingsViewModel.activePackage === modelData.id ? 2 : 1
                            border.color: settingsViewModel.activePackage === modelData.id ? themeBridge.accentStart : themeBridge.border

                            Row {
                                anchors.centerIn: parent
                                spacing: 6

                                Rectangle {
                                    width: 12
                                    height: 12
                                    radius: 6
                                    color: modelData.color
                                    anchors.verticalCenter: parent.verticalCenter
                                }

                                Text {
                                    text: modelData.name
                                    font.pixelSize: 12
                                    font.weight: settingsViewModel.activePackage === modelData.id ? Font.DemiBold : Font.Normal
                                    color: themeBridge.textPrimary
                                    anchors.verticalCenter: parent.verticalCenter
                                }
                            }

                            MouseArea {
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                onClicked: settingsViewModel.setThemePackage(modelData.id)
                            }
                        }
                    }
                }
            }
        }

        // ── 2. Yazı Tipi Bölümü ──────────────────────────────────────────────
        AppCard {
            width: parent.width - 48
            height: 180

            Column {
                anchors.fill: parent
                spacing: 14

                Text {
                    text: i18nBridge.tr("settings_font_section", "Yazı Tipi (Tipografi)")
                    font.pixelSize: 15
                    font.weight: Font.DemiBold
                    color: themeBridge.textPrimary
                }

                Row {
                    spacing: 12

                    Text {
                        text: i18nBridge.tr("settings_font_family", "Yazı Ailesi:")
                        font.pixelSize: 13
                        color: themeBridge.textSecondary
                        anchors.verticalCenter: parent.verticalCenter
                        width: 100
                    }

                    Repeater {
                        model: settingsViewModel.fontFamilies

                        Rectangle {
                            width: 120
                            height: 32
                            radius: 6
                            color: settingsViewRoot.pendingFont === modelData ? themeBridge.surfaceRaised : "transparent"
                            border.width: 1
                            border.color: settingsViewRoot.pendingFont === modelData ? themeBridge.accentStart : themeBridge.border

                            Text {
                                anchors.centerIn: parent
                                text: modelData
                                font.family: modelData
                                font.pixelSize: 12
                                color: themeBridge.textPrimary
                            }

                            MouseArea {
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                onClicked: settingsViewRoot.pendingFont = modelData
                            }
                        }
                    }

                    AppButton {
                        text: i18nBridge.tr("settings_font_apply", "Uygula")
                        variant: "primary"
                        onClicked: settingsViewModel.setFontFamily(settingsViewRoot.pendingFont)
                    }
                }

                // Önizleme Kutusu
                Rectangle {
                    width: parent.width
                    height: 48
                    radius: 8
                    color: themeBridge.background
                    border.width: 1
                    border.color: themeBridge.border

                    Text {
                        anchors.fill: parent
                        anchors.margins: 12
                        text: i18nBridge.tr("settings_font_preview_text", "Hızlı kahverengi tilki — The quick brown fox 0123456789")
                        font.family: settingsViewRoot.pendingFont
                        font.pixelSize: 13
                        color: themeBridge.textPrimary
                        verticalAlignment: Text.AlignVCenter
                    }
                }
            }
        }

        // ── 3. Dil Bölümü ────────────────────────────────────────────────────
        AppCard {
            width: parent.width - 48
            height: 120

            Column {
                anchors.fill: parent
                spacing: 14

                Text {
                    text: i18nBridge.tr("settings_language_section", "Uygulama Dili")
                    font.pixelSize: 15
                    font.weight: Font.DemiBold
                    color: themeBridge.textPrimary
                }

                Row {
                    spacing: 16

                    Text {
                        text: i18nBridge.tr("settings_language_active", "Seçili Dil:")
                        font.pixelSize: 13
                        color: themeBridge.textSecondary
                        anchors.verticalCenter: parent.verticalCenter
                        width: 100
                    }

                    AppButton {
                        text: "🇹🇷 Türkçe"
                        variant: settingsViewModel.currentLanguage === "tr" ? "primary" : "secondary"
                        onClicked: settingsViewModel.setLanguage("tr")
                    }

                    AppButton {
                        text: "🇬🇧 English"
                        variant: settingsViewModel.currentLanguage === "en" ? "primary" : "secondary"
                        onClicked: settingsViewModel.setLanguage("en")
                    }
                }
            }
        }

        // ── 4. Veri Yönetimi ───────────────────────────────────
        AppCard {
            width: parent.width - 48
            height: 110

            Column {
                anchors.fill: parent
                spacing: 14

                Text {
                    text: i18nBridge.tr("settings_data_section", "Veri Yönetimi")
                    font.pixelSize: 15
                    font.weight: Font.DemiBold
                    color: themeBridge.textPrimary
                }

                AppButton {
                    iconName: "upload"
                    text: i18nBridge.tr("settings_export_btn", "Tüm Veriyi Dışa Aktar (.json)")
                    variant: "primary"
                    onClicked: settingsViewModel.exportToJson("")
                }
            }
        }

        // Güncelleme denetimi
        AppButton {
            anchors.horizontalCenter: parent.horizontalCenter
            text: i18nBridge.tr("settings_update_check", "Güncellemeleri Denetle")
            variant: "secondary"
            onClicked: updateViewModel.checkForUpdates()
        }

        // Sürüm Bilgisi
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: settingsViewModel.appName + "  —  v" + settingsViewModel.appVersion
            font.pixelSize: 12
            color: themeBridge.textMuted
        }
    }
}
