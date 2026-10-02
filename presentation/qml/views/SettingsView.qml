import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"

ScrollView {
    id: settingsViewRoot
    anchors.fill: parent
    contentWidth: availableWidth
    clip: true

    Column {
        width: parent.width
        padding: 24
        spacing: 20

        Text {
            text: i18nBridge.tr("settings_title", "Uygulama Ayarları")
            font.pixelSize: 18
            font.weight: Font.DemiBold
            color: themeBridge.textPrimary
        }

        // Görünüm / Tema Ayarı
        AppCard {
            width: parent.width - 48
            height: 120

            Column {
                anchors.fill: parent
                spacing: 12

                Text {
                    text: i18nBridge.tr("settings_appearance", "Görünüm ve Tema")
                    font.pixelSize: 14
                    font.weight: Font.DemiBold
                    color: themeBridge.textPrimary
                }

                Row {
                    spacing: 12
                    AppButton {
                        variant: themeBridge.isDark ? "primary" : "secondary"
                        text: "🌙 " + i18nBridge.tr("theme_dark", "Koyu Tema")
                        onClicked: if (!themeBridge.isDark) themeBridge.toggleTheme()
                    }
                    AppButton {
                        variant: !themeBridge.isDark ? "primary" : "secondary"
                        text: "☀️ " + i18nBridge.tr("theme_light", "Açık Tema")
                        onClicked: if (themeBridge.isDark) themeBridge.toggleTheme()
                    }
                }
            }
        }

        // Dil Ayarı
        AppCard {
            width: parent.width - 48
            height: 120

            Column {
                anchors.fill: parent
                spacing: 12

                Text {
                    text: i18nBridge.tr("settings_language", "Uygulama Dili")
                    font.pixelSize: 14
                    font.weight: Font.DemiBold
                    color: themeBridge.textPrimary
                }

                Row {
                    spacing: 12
                    AppButton {
                        variant: i18nBridge.currentLanguage === "tr" ? "primary" : "secondary"
                        text: "🇹🇷 Türkçe"
                        onClicked: i18nBridge.setLanguage("tr")
                    }
                    AppButton {
                        variant: i18nBridge.currentLanguage === "en" ? "primary" : "secondary"
                        text: "🇬🇧 English"
                        onClicked: i18nBridge.setLanguage("en")
                    }
                }
            }
        }
    }
}
