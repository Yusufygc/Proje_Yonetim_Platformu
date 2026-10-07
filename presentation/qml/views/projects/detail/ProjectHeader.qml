import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../../components"
import "../../../theme"

// Proje başlığı, eylemler, rozetler, açıklama ve bağlantılar.
Column {
    id: root

    property var project: ({})
    spacing: 16

    // Üst Başlık ve Eylemler Satırı
    Row {
        width: parent.width
        spacing: 16

        Text {
            width: parent.width - actionsRow.width - 16
            text: root.project.title || ""
            font.pixelSize: 20
            font.weight: Font.Bold
            color: themeBridge.textPrimary
            wrapMode: Text.Wrap
            anchors.verticalCenter: parent.verticalCenter
        }

        Row {
            id: actionsRow
            spacing: 8
            anchors.verticalCenter: parent.verticalCenter

            AppButton {
                variant: "primary"
                text: i18nBridge.tr("action_edit", "Düzenle")
                iconName: "pencil"
                onClicked: projectViewModel.openEditDialog(root.project.id)
            }

            AppButton {
                variant: "secondary"
                text: root.project.is_archived ? i18nBridge.tr("action_restore", "Geri Yükle") : i18nBridge.tr("action_archive", "Arşivle")
                iconName: "archive"
                onClicked: {
                    if (root.project.is_archived) {
                        projectViewModel.restoreProject(root.project.id);
                    } else {
                        projectViewModel.archiveProject(root.project.id);
                    }
                }
            }

            AppButton {
                variant: "danger"
                text: i18nBridge.tr("action_delete", "Sil")
                iconName: "trash"
                onClicked: projectViewModel.deleteProject(root.project.id)
            }
        }
    }

    // Rozetler Satırı
    Row {
        width: parent.width
        spacing: 10

        StatusIndicator {
            status: root.project.status || "PLANNED"
            anchors.verticalCenter: parent.verticalCenter
        }

        AppBadge {
            text: {
                switch (root.project.priority) {
                    case "CRITICAL": return i18nBridge.tr("priority_critical", "Kritik");
                    case "HIGH": return i18nBridge.tr("priority_high", "Yüksek");
                    case "LOW": return i18nBridge.tr("priority_low", "Düşük");
                    default: return i18nBridge.tr("priority_medium", "Orta");
                }
            }
            badgeColor: {
                switch (root.project.priority) {
                    case "CRITICAL": return themeBridge.danger;
                    case "HIGH": return themeBridge.warning;
                    case "LOW": return themeBridge.textSecondary;
                    default: return themeBridge.accentStart;
                }
            }
            anchors.verticalCenter: parent.verticalCenter
        }

        AppBadge {
            visible: (root.project.health || "") !== ""
            text: {
                switch (root.project.health) {
                    case "GOOD": return i18nBridge.tr("health_good", "Yolunda");
                    case "AT_RISK": return i18nBridge.tr("health_at_risk", "Riskli");
                    case "BLOCKED": return i18nBridge.tr("health_blocked", "Tıkandı");
                    default: return i18nBridge.tr("health_unknown", "Belirsiz");
                }
            }
            badgeColor: root.project.health === "GOOD" ? themeBridge.success : (
                root.project.health === "AT_RISK" ? themeBridge.warning : themeBridge.danger
            )
            anchors.verticalCenter: parent.verticalCenter
        }

        AppBadge {
            visible: (root.project.project_type || "") !== ""
            text: {
                var pt = (root.project.project_type || "").toUpperCase();
                switch (pt) {
                    case "SOFTWARE": case "YAZILIM": return i18nBridge.tr("project_type_software", "Yazılım");
                    case "EDUCATION": case "EGITIM": case "EĞİTİM": return i18nBridge.tr("project_type_education", "Eğitim");
                    case "RESEARCH": case "ARASTIRMA": case "ARAŞTIRMA": return i18nBridge.tr("project_type_research", "Araştırma");
                    case "DESIGN": case "TASARIM": return i18nBridge.tr("project_type_design", "Tasarım");
                    case "INTERNAL": case "IC ARAC": case "İÇ ARAÇ": return i18nBridge.tr("project_type_internal", "İç Araç");
                    case "CLIENT": case "MUSTERI": case "MÜŞTERİ İŞİ": return i18nBridge.tr("project_type_client", "Müşteri İşi");
                    case "EXPERIMENTAL": case "DENEYSEL": return i18nBridge.tr("project_type_experimental", "Deneysel");
                    case "WEB": return "Web";
                    case "MOBILE": return "Mobil";
                    case "DESKTOP": return "Masaüstü";
                    case "CLI": return "Komut Satırı";
                    case "OTHER": case "DIGER": case "DİĞER": return i18nBridge.tr("project_type_other", "Diğer");
                    default: return root.project.project_type || "";
                }
            }
            badgeColor: themeBridge.textSecondary
            anchors.verticalCenter: parent.verticalCenter
        }

        Item { width: 1; height: 1; Layout.fillWidth: true }

        AppProgressBar {
            value: root.project.progress || 0
            showLabel: true
            barHeight: 6
            implicitWidth: 100
            anchors.verticalCenter: parent.verticalCenter
        }
    }

    // Açıklama
    AppCard {
        width: parent.width
        height: Math.max(70, descText.implicitHeight + 32)
        visible: (root.project.description || "") !== ""

        Column {
            anchors.fill: parent
            spacing: 4

            Text {
                text: i18nBridge.tr("section_description", "AÇIKLAMA")
                font.pixelSize: 11
                font.weight: Font.DemiBold
                color: themeBridge.textMuted
            }

            Text {
                id: descText
                text: root.project.description || ""
                font.pixelSize: 13
                color: themeBridge.textSecondary
                wrapMode: Text.Wrap
                width: parent.width
            }
        }
    }

    // Bağlantılar (GitHub / Klasör)
    Row {
        width: parent.width
        spacing: 12
        visible: (root.project.github_repo || "") !== "" || (root.project.local_path || "") !== ""

        AppButton {
            visible: (root.project.github_repo || "") !== ""
            variant: "secondary"
            text: "GitHub Deposu"
            iconName: "external-link"
            onClicked: projectSubitemsViewModel.openUrlOrPath(root.project.github_repo)
        }

        AppButton {
            visible: (root.project.local_path || "") !== ""
            variant: "secondary"
            text: "Yerel Klasör"
            iconName: "folder"
            onClicked: projectSubitemsViewModel.openUrlOrPath(root.project.local_path)
        }
    }
}
