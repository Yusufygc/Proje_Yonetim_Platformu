import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

import "shell"
import "components"

ApplicationWindow {
    id: appWindow

    visible: true
    width: 1280
    height: 800
    minimumWidth: 1024
    minimumHeight: 680

    title: i18nBridge.tr("app_name", "Proje Takip Platformu")
    color: themeBridge.background

    // Genişlik < 980 olduğunda sidebar otomatik daralır (MainWindow davranışı)
    onWidthChanged: {
        if (width < 980 && !navBridge.sidebarCollapsed) {
            navBridge.setSidebarCollapsed(true);
        }
    }

    // Kısayollar: Ctrl+F, Ctrl+K, Ctrl+N
    Shortcut {
        sequence: "Ctrl+F"
        onActivated: navBridge.openSearch()
    }

    Shortcut {
        sequence: "Ctrl+K"
        onActivated: navBridge.openSearch()
    }

    Shortcut {
        sequence: "Ctrl+N"
        onActivated: navBridge.createNewProject()
    }

    // Ana Ekran Düzeni: Sol Sidebar + Sağ İçerik
    Row {
        anchors.fill: parent

        // Sol Sidebar
        Sidebar {
            id: mainSidebar
            height: parent.height
        }

        // Sağ İçerik Bölümü (Header + Dinamik Sayfa)
        Column {
            width: parent.width - mainSidebar.width
            height: parent.height

            TopHeader {
                width: parent.width
            }

            // Sayfa Yükleyici (Loader)
            Item {
                width: parent.width
                height: parent.height - 56
                clip: true

                Loader {
                    id: pageLoader
                    anchors.fill: parent
                    asynchronous: true
                    source: {
                        switch (navBridge.currentPage) {
                            case "dashboard": return "views/DashboardView.qml";
                            case "projects": return "views/ProjectsView.qml";
                            case "ideas": return "views/IdeasView.qml";
                            case "tasks": return "views/TasksView.qml";
                            case "memo": return "views/MemoView.qml";
                            case "analytics": return "views/AnalyticsView.qml";
                            case "archive": return "views/ArchiveView.qml";
                            case "info": return "views/InfoView.qml";
                            case "settings": return "views/SettingsView.qml";
                            default: return "views/DashboardView.qml";
                        }
                    }
                }
            }
        }
    }

    // Toast Bildirim Bileşeni
    ToastNotification {
        anchors.horizontalCenter: parent.horizontalCenter
        z: 999
    }

    // Küresel Hızlı Arama Modalı (Ctrl+K / Ctrl+F)
    GlobalSearchModal {
        anchors.fill: parent
    }
}
