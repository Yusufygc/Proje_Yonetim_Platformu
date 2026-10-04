import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"

ScrollView {
    id: analyticsViewRoot
    anchors.fill: parent
    contentWidth: availableWidth
    clip: true

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

            // Proje Filtresi
            Rectangle {
                id: projSelectBox
                width: 220
                height: 36
                radius: 8
                color: themeBridge.surface
                border.width: 1
                border.color: projMouse.containsMouse || projMenu.opened ? themeBridge.accentStart : themeBridge.border

                Row {
                    anchors.fill: parent
                    anchors.leftMargin: 12
                    anchors.rightMargin: 12
                    spacing: 8

                    AppIcon {
                        name: "folder"
                        size: 14
                        color: themeBridge.accentStart
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    Text {
                        width: parent.width - 44
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
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    Text {
                        text: "▼"
                        font.pixelSize: 10
                        color: themeBridge.textMuted
                        anchors.verticalCenter: parent.verticalCenter
                    }
                }

                MouseArea {
                    id: projMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: projMenu.open()
                }

                Menu {
                    id: projMenu
                    y: projSelectBox.height + 4
                    width: projSelectBox.width

                    background: Rectangle {
                        radius: 8
                        color: themeBridge.surface
                        border.width: 1
                        border.color: themeBridge.border
                    }

                    Repeater {
                        model: analyticsViewModel.projects
                        MenuItem {
                            text: modelData.title
                            onTriggered: analyticsViewModel.setProjectId(modelData.id)
                        }
                    }
                }
            }
        }

        // ── KPI Kartları ───────────────────────────────────────────────────
        Row {
            width: parent.width - 48
            spacing: 12

            // Kart 1: Tamamlanan
            AppCard {
                width: (parent.width - 48) / 5
                height: 100

                Column {
                    anchors.centerIn: parent
                    spacing: 4

                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: i18nBridge.tr("analytics_kpi_total_completed", "Tamamlanan")
                        font.pixelSize: 12
                        color: themeBridge.textSecondary
                    }
                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: analyticsViewModel.totalCompleted.toString()
                        font.pixelSize: 24
                        font.weight: Font.Bold
                        color: themeBridge.accentStart
                    }
                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: i18nBridge.tr("analytics_kpi_total_completed_desc", "Dönemde biten")
                        font.pixelSize: 11
                        color: themeBridge.textMuted
                    }
                }
            }

            // Kart 2: Tamamlanma Oranı
            AppCard {
                width: (parent.width - 48) / 5
                height: 100

                Column {
                    anchors.centerIn: parent
                    spacing: 4

                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: i18nBridge.tr("analytics_kpi_completion_rate", "Oran %")
                        font.pixelSize: 12
                        color: themeBridge.textSecondary
                    }
                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: analyticsViewModel.completionRate.toFixed(1) + " %"
                        font.pixelSize: 24
                        font.weight: Font.Bold
                        color: "#10B981"
                    }
                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: i18nBridge.tr("analytics_kpi_completion_rate_desc", "Biten / Toplam")
                        font.pixelSize: 11
                        color: themeBridge.textMuted
                    }
                }
            }

            // Kart 3: Seri (Streak)
            AppCard {
                width: (parent.width - 48) / 5
                height: 100

                Column {
                    anchors.centerIn: parent
                    spacing: 4

                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: i18nBridge.tr("analytics_kpi_streak_days", "Seri (Gün)")
                        font.pixelSize: 12
                        color: themeBridge.textSecondary
                    }
                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: analyticsViewModel.streakDays.toString()
                        font.pixelSize: 24
                        font.weight: Font.Bold
                        color: "#F59E0B"
                    }
                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: i18nBridge.tr("analytics_kpi_streak_days_desc", "Aktif gün")
                        font.pixelSize: 11
                        color: themeBridge.textMuted
                    }
                }
            }

            // Kart 4: Zamanında Bitirme
            AppCard {
                width: (parent.width - 48) / 5
                height: 100

                Column {
                    anchors.centerIn: parent
                    spacing: 4

                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: i18nBridge.tr("analytics_kpi_on_time_rate", "Zamanında %")
                        font.pixelSize: 12
                        color: themeBridge.textSecondary
                    }
                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: analyticsViewModel.onTimeRate.toFixed(1) + " %"
                        font.pixelSize: 24
                        font.weight: Font.Bold
                        color: "#6366F1"
                    }
                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: i18nBridge.tr("analytics_kpi_on_time_rate_desc", "Vadesinde biten")
                        font.pixelSize: 11
                        color: themeBridge.textMuted
                    }
                }
            }

            // Kart 5: En İyi Dönem
            AppCard {
                width: (parent.width - 48) / 5
                height: 100

                Column {
                    anchors.centerIn: parent
                    spacing: 4

                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: i18nBridge.tr("analytics_kpi_best_period", "En İyi Dönem")
                        font.pixelSize: 12
                        color: themeBridge.textSecondary
                    }
                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: analyticsViewModel.bestPeriodLabel
                        font.pixelSize: 16
                        font.weight: Font.Bold
                        color: themeBridge.textPrimary
                        elide: Text.ElideRight
                    }
                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: "(" + analyticsViewModel.bestPeriodCount + " görev)"
                        font.pixelSize: 11
                        color: themeBridge.textMuted
                    }
                }
            }
        }

        // ── Ana Grafik: Zaman Serisi ─────────────────────────────────────────
        AppCard {
            width: parent.width - 48
            height: 240

            Column {
                anchors.fill: parent
                spacing: 12

                Text {
                    text: i18nBridge.tr("analytics_panel_time_title", "Zaman İçinde Tamamlanan Görevler")
                    font.pixelSize: 14
                    font.weight: Font.DemiBold
                    color: themeBridge.textPrimary
                }

                // Grafik Çizim Alanı
                Item {
                    width: parent.width
                    height: parent.height - 30

                    // Boş durum
                    Text {
                        anchors.centerIn: parent
                        text: i18nBridge.tr("analytics_no_data", "Bu dönemde tamamlanan görev kaydı bulunmuyor.")
                        font.pixelSize: 13
                        color: themeBridge.textMuted
                        visible: analyticsViewModel.timeSeries.length === 0
                    }

                    // Bar Çubukları
                    Row {
                        anchors.fill: parent
                        spacing: Math.max(4, (width - (analyticsViewModel.timeSeries.length * 36)) / Math.max(1, analyticsViewModel.timeSeries.length))
                        visible: analyticsViewModel.timeSeries.length > 0

                        Repeater {
                            model: analyticsViewModel.timeSeries

                            Item {
                                width: 36
                                height: parent.height

                                property int val: modelData.value
                                property int maxVal: {
                                    var m = 1;
                                    for (var i = 0; i < analyticsViewModel.timeSeries.length; i++) {
                                        if (analyticsViewModel.timeSeries[i].value > m) {
                                            m = analyticsViewModel.timeSeries[i].value;
                                        }
                                    }
                                    return m;
                                }

                                Column {
                                    anchors.fill: parent
                                    spacing: 4

                                    // Çubuk Alanı
                                    Item {
                                        width: parent.width
                                        height: parent.height - 24

                                        Rectangle {
                                            width: 24
                                            anchors.horizontalCenter: parent.horizontalCenter
                                            anchors.bottom: parent.bottom
                                            height: Math.max(4, (parent.height - 16) * (modelData.value / Math.max(1, maxVal)))
                                            radius: 4
                                            color: barMouse.containsMouse ? themeBridge.accentEnd : themeBridge.accentStart

                                            Behavior on height {
                                                NumberAnimation { duration: 250; easing.type: Easing.OutQuad }
                                            }

                                            Text {
                                                anchors.horizontalCenter: parent.horizontalCenter
                                                anchors.bottom: parent.top
                                                anchors.bottomMargin: 2
                                                text: modelData.value.toString()
                                                font.pixelSize: 10
                                                font.weight: Font.DemiBold
                                                color: themeBridge.textPrimary
                                                visible: modelData.value > 0 || barMouse.containsMouse
                                            }
                                        }

                                        MouseArea {
                                            id: barMouse
                                            anchors.fill: parent
                                            hoverEnabled: true
                                        }
                                    }

                                    // Etiket
                                    Text {
                                        anchors.horizontalCenter: parent.horizontalCenter
                                        text: modelData.label
                                        font.pixelSize: 10
                                        color: themeBridge.textSecondary
                                        elide: Text.ElideRight
                                        width: parent.width
                                        horizontalAlignment: Text.AlignHCenter
                                    }
                                }
                            }
                        }
                    }
                }
            }
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
