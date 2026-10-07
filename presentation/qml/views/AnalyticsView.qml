import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../components"
import "analytics"

ScrollView {
    id: analyticsViewRoot
    anchors.fill: parent
    contentWidth: availableWidth
    clip: true

    ScrollBar.vertical: AppScrollBar { }

    Column {
        width: parent.width
        padding: 24
        spacing: 20

        // ── Başlık ve Filtreler ─────────────────────────────────────────────
        Row {
            width: parent.width - 48
            spacing: 16

            Column {
                spacing: 4
                Text {
                    text: i18nBridge.tr("analytics_title", "Analitik & Metrikler")
                    font.pixelSize: 22
                    font.weight: Font.Bold
                    color: themeBridge.textPrimary
                }
                Text {
                    text: i18nBridge.tr("analytics_subtitle", "Tamamlanan görevlerin ve projelerin performans analizi")
                    font.pixelSize: 13
                    color: themeBridge.textSecondary
                }
            }
        }

        // Dönem ve Proje Filtre Satırı
        Row {
            width: parent.width - 48
            spacing: 12

            // Dönem Butonları
            Row {
                spacing: 6

                Repeater {
                    model: [
                        { key: "daily", label: i18nBridge.tr("analytics_period_daily", "Günlük") },
                        { key: "weekly", label: i18nBridge.tr("analytics_period_weekly", "Haftalık") },
                        { key: "monthly", label: i18nBridge.tr("analytics_period_monthly", "Aylık") },
                        { key: "yearly", label: i18nBridge.tr("analytics_period_yearly", "Yıllık") }
                    ]

                    AppButton {
                        text: modelData.label
                        variant: analyticsViewModel.period === modelData.key ? "primary" : "secondary"
                        onClicked: analyticsViewModel.setPeriod(modelData.key)
                    }
                }
            }

            Item { width: 20; height: 1 }

            ProjectFilter { }
        }

        // ── KPI Kartları ───────────────────────────────────────────────────
        Row {
            width: parent.width - 48
            spacing: 12

            KpiCard {
                width: (parent.width - 48) / 5
                label: i18nBridge.tr("analytics_kpi_total_completed", "Tamamlanan")
                value: analyticsViewModel.totalCompleted.toString()
                description: i18nBridge.tr("analytics_kpi_total_completed_desc", "Dönemde biten")
            }
            KpiCard {
                width: (parent.width - 48) / 5
                label: i18nBridge.tr("analytics_kpi_completion_rate", "Oran %")
                value: analyticsViewModel.completionRate.toFixed(1) + " %"
                description: i18nBridge.tr("analytics_kpi_completion_rate_desc", "Biten / Toplam")
                valueColor: themeBridge.success
            }
            KpiCard {
                width: (parent.width - 48) / 5
                label: i18nBridge.tr("analytics_kpi_streak_days", "Seri (Gün)")
                value: analyticsViewModel.streakDays.toString()
                description: i18nBridge.tr("analytics_kpi_streak_days_desc", "Aktif gün")
                valueColor: themeBridge.warning
            }
            KpiCard {
                width: (parent.width - 48) / 5
                label: i18nBridge.tr("analytics_kpi_on_time_rate", "Zamanında %")
                value: analyticsViewModel.onTimeRate.toFixed(1) + " %"
                description: i18nBridge.tr("analytics_kpi_on_time_rate_desc", "Vadesinde biten")
            }
            KpiCard {
                width: (parent.width - 48) / 5
                label: i18nBridge.tr("analytics_kpi_best_period", "En İyi Dönem")
                value: analyticsViewModel.bestPeriodLabel
                description: "(" + analyticsViewModel.bestPeriodCount + " görev)"
                valueColor: themeBridge.textPrimary
                valueSize: 16
            }
        }

        TimeSeriesChart {
            width: parent.width - 48
        }

        // ── Alt Grafikler: Öncelik ve Proje Dağılımı ─────────────────────────
        Row {
            width: parent.width - 48
            spacing: 16

            // Öncelik Dağılım Kartı
            AppCard {
                width: (parent.width - 16) / 2
                height: 220

                Column {
                    anchors.fill: parent
                    spacing: 12

                    Text {
                        text: i18nBridge.tr("analytics_panel_priority_title", "Öncelik Dağılımı")
                        font.pixelSize: 14
                        font.weight: Font.DemiBold
                        color: themeBridge.textPrimary
                    }

                    Repeater {
                        model: analyticsViewModel.priorityDistribution

                        Column {
                            width: parent.width
                            spacing: 4

                            Row {
                                width: parent.width
                                spacing: 8

                                Rectangle {
                                    width: 10
                                    height: 10
                                    radius: 5
                                    color: modelData.color
                                    anchors.verticalCenter: parent.verticalCenter
                                }

                                Text {
                                    text: modelData.label
                                    font.pixelSize: 12
                                    font.weight: Font.Medium
                                    color: themeBridge.textPrimary
                                    width: parent.width - 120
                                    anchors.verticalCenter: parent.verticalCenter
                                }

                                Text {
                                    text: modelData.value + " görev"
                                    font.pixelSize: 12
                                    font.weight: Font.DemiBold
                                    color: themeBridge.textSecondary
                                    anchors.verticalCenter: parent.verticalCenter
                                }
                            }

                            // Dağılım Barı
                            Rectangle {
                                width: parent.width
                                height: 6
                                radius: 3
                                color: themeBridge.background

                                Rectangle {
                                    width: {
                                        var total = analyticsViewModel.totalCompleted;
                                        return total > 0 ? (parent.width * (modelData.value / total)) : 0;
                                    }
                                    height: parent.height
                                    radius: 3
                                    color: modelData.color
                                }
                            }
                        }
                    }
                }
            }

            // Proje Dağılım Kartı
            AppCard {
                width: (parent.width - 16) / 2
                height: 220

                Column {
                    anchors.fill: parent
                    spacing: 12

                    Text {
                        text: i18nBridge.tr("analytics_panel_project_title", "Proje Dağılımı")
                        font.pixelSize: 14
                        font.weight: Font.DemiBold
                        color: themeBridge.textPrimary
                    }

                    Text {
                        text: i18nBridge.tr("analytics_no_project_dist", "Tamamlanan proje görevi bulunmuyor.")
                        font.pixelSize: 12
                        color: themeBridge.textMuted
                        visible: analyticsViewModel.projectDistribution.length === 0
                    }

                    Repeater {
                        model: analyticsViewModel.projectDistribution.slice(0, 4)

                        Column {
                            width: parent.width
                            spacing: 4

                            Row {
                                width: parent.width
                                spacing: 8

                                Text {
                                    text: modelData.title
                                    font.pixelSize: 12
                                    font.weight: Font.Medium
                                    color: themeBridge.textPrimary
                                    elide: Text.ElideRight
                                    width: parent.width - 100
                                }

                                Text {
                                    text: modelData.count + " görev"
                                    font.pixelSize: 12
                                    font.weight: Font.DemiBold
                                    color: themeBridge.accentStart
                                }
                            }

                            // Proje Barı
                            Rectangle {
                                width: parent.width
                                height: 6
                                radius: 3
                                color: themeBridge.background

                                Rectangle {
                                    width: {
                                        var maxP = 1;
                                        var pDist = analyticsViewModel.projectDistribution;
                                        for (var j = 0; j < pDist.length; j++) {
                                            if (pDist[j].count > maxP) maxP = pDist[j].count;
                                        }
                                        return parent.width * (modelData.count / maxP);
                                    }
                                    height: parent.height
                                    radius: 3
                                    color: "#6366F1"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
