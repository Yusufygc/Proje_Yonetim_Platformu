import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"

Column {
    id: root

    property string label: ""
    property var model: []
    property int currentIndex: 0
    property var selectedValue: null
    property alias currentValue: root.selectedValue

    signal valueSelected(var value)

    width: parent ? parent.width : 200
    spacing: 6

    function _getItemText(item) {
        if (item === undefined || item === null) return "";
        if (typeof item === "object" && item.text !== undefined) return item.text;
        return String(item);
    }

    function _getItemValue(item) {
        if (item === undefined || item === null) return null;
        if (typeof item === "object" && item.value !== undefined) return item.value;
        return item;
    }

    onSelectedValueChanged: {
        if (!model || model.length === 0) return;
        for (var i = 0; i < model.length; i++) {
            if (_getItemValue(model[i]) == selectedValue) {
                if (currentIndex !== i) {
                    currentIndex = i;
                }
                return;
            }
        }
    }

    onCurrentIndexChanged: {
        if (!model || model.length === 0) return;
        var item = model[currentIndex];
        var val = _getItemValue(item);
        if (selectedValue !== val) {
            selectedValue = val;
            valueSelected(val);
        }
    }

    onModelChanged: {
        if (selectedValue !== null && selectedValue !== undefined) {
            for (var i = 0; i < model.length; i++) {
                if (_getItemValue(model[i]) == selectedValue) {
                    currentIndex = i;
                    return;
                }
            }
        }
        if (model && model.length > 0 && (currentIndex >= 0 && currentIndex < model.length)) {
            var item = model[currentIndex];
            selectedValue = _getItemValue(item);
        }
    }

    Text {
        visible: root.label !== ""
        text: root.label
        font.pixelSize: 12
        font.weight: Font.Medium
        color: themeBridge.textSecondary
    }

    Rectangle {
        id: selectorBox
        width: parent.width
        height: 38
        radius: 8
        color: themeBridge.background
        border.width: 1
        border.color: comboMouse.containsMouse || menuPopup.opened ? themeBridge.accentStart : themeBridge.border

        Row {
            anchors.fill: parent
            anchors.leftMargin: 12
            anchors.rightMargin: 12
            spacing: 8

            Text {
                width: parent.width - 24
                text: root.model && root.model.length > root.currentIndex ? root._getItemText(root.model[root.currentIndex]) : ""
                font.pixelSize: 13
                color: themeBridge.textPrimary
                anchors.verticalCenter: parent.verticalCenter
                elide: Text.ElideRight
            }

            Text {
                text: "▼"
                font.pixelSize: 10
                color: themeBridge.textMuted
                anchors.verticalCenter: parent.verticalCenter
            }
        }

        MouseArea {
            id: comboMouse
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: menuPopup.open()
        }

        Menu {
            id: menuPopup
            y: selectorBox.height + 4
            width: selectorBox.width

            background: Rectangle {
                radius: 8
                color: themeBridge.surface
                border.width: 1
                border.color: themeBridge.border
            }

            Repeater {
                model: root.model
                MenuItem {
                    text: root._getItemText(modelData)
                    onTriggered: {
                        root.currentIndex = index;
                        root.selectedValue = root._getItemValue(modelData);
                        root.valueSelected(root.selectedValue);
                    }
                }
            }
        }
    }
}
