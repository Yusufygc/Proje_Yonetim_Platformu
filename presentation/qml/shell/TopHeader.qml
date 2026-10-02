import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"

Rectangle {
    id: headerRoot

    height: 56
    color: themeBridge.surface
    border.width: 1
    border.color: themeBridge.border

    Row {
        anchors.left: parent.left
        anchors.leftMargin: 24
        anchors.verticalCenter: parent.verticalCenter
        spacing: 12

        Text {
            id: pageTitle
            text: {
                var currentKey = navBridge.currentPage;
                var mods = navBridge.modules;
                for (var i = 0; i < mods.length; i++) {
                    if (mods[i].page_key === currentKey) {
                        return i18nBridge.tr(mods[i].label_key, mods[i].default_label);
                    }
                }
                return currentKey.toUpperCase();
            }
            font.pixelSize: 18
            font.weight: Font.DemiBold
            color: themeBridge.textPrimary
            anchors.verticalCenter: parent.verticalCenter
        }
    }

    Row {
        anchors.right: parent.right
        anchors.rightMargin: 24
        anchors.verticalCenter: parent.verticalCenter
        spacing: 12

        // Yeni Proje Butonu
        AppButton {
            variant: "primary"
            text: i18nBridge.tr("btn_new_project", "Yeni Proje")
            iconName: "folder"
            onClicked: navBridge.createNewProject()
            anchors.verticalCenter: parent.verticalCenter
        }
    }
}
