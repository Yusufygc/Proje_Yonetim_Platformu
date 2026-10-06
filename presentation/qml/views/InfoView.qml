import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"
import "../theme"

ScrollView {
    id: infoViewRoot
    anchors.fill: parent
    contentWidth: availableWidth
    clip: true

    ScrollBar.vertical: AppScrollBar { }

    Column {
        width: parent.width
        padding: 24
        spacing: 24

        // ── 1. Hero Bölümü ──────────────────────────────────────────────────
        AppCard {
            width: parent.width - 48
            height: 180

            Column {
                anchors.centerIn: parent
                spacing: 8

                AppIcon {
                    name: "circle-info"
                    size: 40
                    color: themeBridge.accentStart
                    anchors.horizontalCenter: parent.horizontalCenter
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: i18nBridge.tr("app_name", "Proje Yönetim ve Takip Platformu")
                    font.pixelSize: 22
                    font.weight: Font.Bold
                    color: themeBridge.textPrimary
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: "v" + settingsViewModel.appVersion + " — PySide6 & QML Modern Mimarisi"
                    font.pixelSize: 12
                    color: themeBridge.textMuted
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: i18nBridge.tr(
                        "info_tagline",
                        "Yazılım projelerinizi, fikirlerinizi ve görevlerinizi tek merkezden modern hızda yönetin."
                    )
                    font.pixelSize: 13
                    color: themeBridge.textSecondary
                }
            }
        }

        // ── 2. Çalışma Akışı ────────────────────────────────────────────────
        Column {
            width: parent.width - 48
            spacing: 12

            Text {
                text: i18nBridge.tr("info_workflow_title", "Çalışma Akışı")
                font.pixelSize: 16
                font.weight: Font.DemiBold
                color: themeBridge.textPrimary
            }

            Row {
                width: parent.width
                spacing: 12

                // Adım 1: Fikir Havuzu
                AppCard {
                    width: (parent.width - 24) / 3
                    height: 100

                    Column {
                        anchors.centerIn: parent
                        spacing: 8
                        AppIcon {
                            name: "lightbulb"
                            size: 24
                            color: themeBridge.warning
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: i18nBridge.tr("info_flow_ideas", "1. Fikir Havuzu")
                            font.pixelSize: 13
                            font.weight: Font.DemiBold
                            color: themeBridge.textPrimary
                        }
                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: i18nBridge.tr("info_flow_ideas_sub", "Fikirleri topla ve puanla")
                            font.pixelSize: 11
                            color: themeBridge.textSecondary
                        }
                    }
                }

                // Adım 2: Projeler
                AppCard {
                    width: (parent.width - 24) / 3
                    height: 100

                    Column {
                        anchors.centerIn: parent
                        spacing: 8
                        AppIcon {
                            name: "folder"
                            size: 24
                            color: themeBridge.accentStart
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: i18nBridge.tr("info_flow_projects", "2. Projeler")
                            font.pixelSize: 13
                            font.weight: Font.DemiBold
                            color: themeBridge.textPrimary
                        }
                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: i18nBridge.tr("info_flow_projects_sub", "Aşamalara göre takip et")
                            font.pixelSize: 11
                            color: themeBridge.textSecondary
                        }
                    }
                }

                // Adım 3: Görevler
                AppCard {
                    width: (parent.width - 24) / 3
                    height: 100

                    Column {
                        anchors.centerIn: parent
                        spacing: 8
                        AppIcon {
                            name: "check-square"
                            size: 24
                            color: themeBridge.success
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: i18nBridge.tr("info_flow_tasks", "3. Görevler (WBS)")
                            font.pixelSize: 13
                            font.weight: Font.DemiBold
                            color: themeBridge.textPrimary
                        }
                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: i18nBridge.tr("info_flow_tasks_sub", "Kırılımları tamamla")
                            font.pixelSize: 11
                            color: themeBridge.textSecondary
                        }
                    }
                }
            }
        }

        // ── 3. Sistem Bileşenleri ───────────────────────────────────────────
        Column {
            width: parent.width - 48
            spacing: 12

            Text {
                text: i18nBridge.tr("info_features_title", "Sistem Bileşenleri")
                font.pixelSize: 16
                font.weight: Font.DemiBold
                color: themeBridge.textPrimary
            }

            Grid {
                width: parent.width
                columns: 2
                spacing: 12

                Repeater {
                    model: [
                        {
                            icon: "home",
                            color: themeBridge.accentStart,
                            title: i18nBridge.tr("nav_dashboard", "Dashboard"),
                            desc: i18nBridge.tr("info_feat_dashboard_desc", "Proje sayıları, bekleyen ve tamamlanan görevler, tıkanan işler tek bakışta.")
                        },
                        {
                            icon: "folder",
                            color: themeBridge.accentStart,
                            title: i18nBridge.tr("nav_projects", "Projeler"),
                            desc: i18nBridge.tr("info_feat_projects_desc", "Planlandı → Geliştirme → Test → Tamamlandı aşamaları, kararlar ve kaynaklar.")
                        },
                        {
                            icon: "check-square",
                            color: themeBridge.success,
                            title: i18nBridge.tr("nav_tasks", "Görevler (WBS)"),
                            desc: i18nBridge.tr("info_feat_tasks_desc", "Hiyerarşik iş kırılımı, ilerleme çubukları, durum ve öncelik filtreleri.")
                        },
                        {
                            icon: "lightbulb",
                            color: themeBridge.warning,
                            title: i18nBridge.tr("nav_ideas", "Fikir Havuzu"),
                            desc: i18nBridge.tr("info_feat_ideas_desc", "Ham fikirleri kaydedin, puanlayın ve tek tıkla doğrudan projeye dönüştürün.")
                        },
                        {
                            icon: "note-sticky",
                            color: "#EC4899",
                            title: i18nBridge.tr("nav_notes", "Notlarım (Memo)"),
                            desc: i18nBridge.tr("info_feat_memo_desc", "Zengin metin biçimlendirme ve serbest el çizim tuvali ile renkli yapışkan notlar.")
                        },
                        {
                            icon: "chart-bar",
                            color: themeBridge.accentEnd,
                            title: i18nBridge.tr("nav_analytics", "Analitik"),
                            desc: i18nBridge.tr("info_feat_analytics_desc", "Dönem bazlı tamamlanma grafikleri, başarı oranı ve performans göstergeleri.")
                        }
                    ]

                    AppCard {
                        width: (infoViewRoot.width - 48 - 12) / 2
                        height: 90

                        Row {
                            anchors.fill: parent
                            anchors.margins: 14
                            spacing: 12

                            Rectangle {
                                width: 36
                                height: 36
                                radius: 8
                                color: Theme.accentAlpha(themeBridge.currentTheme, 0.12)
                                anchors.verticalCenter: parent.verticalCenter

                                AppIcon {
                                    name: modelData.icon
                                    size: 18
                                    color: modelData.color
                                    anchors.centerIn: parent
                                }
                            }

                            Column {
                                width: parent.width - 50
                                anchors.verticalCenter: parent.verticalCenter
                                spacing: 2

                                Text {
                                    text: modelData.title
                                    font.pixelSize: 13
                                    font.weight: Font.DemiBold
                                    color: themeBridge.textPrimary
                                }
                                Text {
                                    text: modelData.desc
                                    font.pixelSize: 11
                                    color: themeBridge.textSecondary
                                    wrapMode: Text.WordWrap
                                    width: parent.width
                                    maximumLineCount: 2
                                    elide: Text.ElideRight
                                }
                            }
                        }
                    }
                }
            }
        }

        // ── 4. Kısayollar ve İpuçları ───────────────────────────────────────
        Row {
            width: parent.width - 48
            spacing: 16

            // Kısayollar Kartı
            AppCard {
                width: (parent.width - 16) / 2
                height: 170

                Column {
                    anchors.fill: parent
                    spacing: 12

                    Text {
                        text: i18nBridge.tr("info_shortcuts_title", "Klavye Kısayolları")
                        font.pixelSize: 15
                        font.weight: Font.DemiBold
                        color: themeBridge.textPrimary
                    }

                    Repeater {
                        model: [
                            { key: "Ctrl + F  /  Ctrl + K", desc: i18nBridge.tr("info_sc_search", "Küresel arama kutusunu açar") },
                            { key: "Ctrl + N", desc: i18nBridge.tr("info_sc_new", "Yeni proje veya görev oluşturur") },
                            { key: "ESC", desc: i18nBridge.tr("info_sc_esc", "Açık pencereleri ve aramayı kapatır") }
                        ]

                        Row {
                            width: parent.width
                            spacing: 12

                            Rectangle {
                                width: 140
                                height: 26
                                radius: 4
                                color: themeBridge.background
                                border.width: 1
                                border.color: themeBridge.border

                                Text {
                                    anchors.centerIn: parent
                                    text: modelData.key
                                    font.pixelSize: 11
                                    font.weight: Font.DemiBold
                                    color: themeBridge.accentStart
                                }
                            }

                            Text {
                                text: modelData.desc
                                font.pixelSize: 12
                                color: themeBridge.textSecondary
                                anchors.verticalCenter: parent.verticalCenter
                            }
                        }
                    }
                }
            }

            // Önemli İpuçları Kartı
            AppCard {
                width: (parent.width - 16) / 2
                height: 170

                Column {
                    anchors.fill: parent
                    spacing: 12

                    Text {
                        text: i18nBridge.tr("info_tips_title", "Önemli İpuçları")
                        font.pixelSize: 15
                        font.weight: Font.DemiBold
                        color: themeBridge.textPrimary
                    }

                    Column {
                        spacing: 8
                        width: parent.width

                        Text {
                            text: "• " + i18nBridge.tr("info_tip_1", "Sol alttaki ay düğmesi ile tek tıkla açık/koyu modlar arasında geçiş yapabilirsiniz.")
                            font.pixelSize: 12
                            color: themeBridge.textSecondary
                            wrapMode: Text.WordWrap
                            width: parent.width
                        }

                        Text {
                            text: "• " + i18nBridge.tr("info_tip_2", "Tüm verileriniz SQLite ile yerel bilgisayarınızda güvendedir; internet bağlantısı gerekmez.")
                            font.pixelSize: 12
                            color: themeBridge.textSecondary
                            wrapMode: Text.WordWrap
                            width: parent.width
                        }

                        Text {
                            text: "• " + i18nBridge.tr("info_tip_3", "Ayarlar menüsünden tüm verilerinizi tek tıkla JSON olarak dışa aktarabilirsiniz.")
                            font.pixelSize: 12
                            color: themeBridge.textSecondary
                            wrapMode: Text.WordWrap
                            width: parent.width
                        }
                    }
                }
            }
        }

        // Alt Bilgi
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: settingsViewModel.appName + "  ·  v" + settingsViewModel.appVersion
            font.pixelSize: 11
            color: themeBridge.textMuted
        }
    }
}
