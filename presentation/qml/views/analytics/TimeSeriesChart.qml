import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../components"

// Dönem içinde tamamlanan görevlerin çubuk grafiği.
AppCard {
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
