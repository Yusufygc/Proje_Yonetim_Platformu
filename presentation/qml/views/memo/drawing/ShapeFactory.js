.pragma library

// Fare bırakıldığında sürükleme durumundan yeni tuval öğesi üretir; uygun değilse null döner.
// `s`: { color, lineWidth, startX, startY, currentX, currentY, points, fillEnabled }
// `fill`: çizgi renginden dolgu rengi üreten fonksiyon.

// Akış şeması blokları: asgari boyut ve varsayılan metin.
var FLOW_BLOCKS = {
    flow_start: { minW: 40, minH: 26, text: "Başla" },
    flow_process: { minW: 50, minH: 30, text: "İşlem" },
    flow_decision: { minW: 50, minH: 36, text: "Koşul ?" },
    flow_io: { minW: 50, minH: 30, text: "Girdi / Çıktı" }
}

function createItem(tool, s, fill) {
    var dx = Math.abs(s.currentX - s.startX)
    var dy = Math.abs(s.currentY - s.startY)
    var x = Math.min(s.startX, s.currentX)
    var y = Math.min(s.startY, s.currentY)
    var style = { color: s.color, width: s.lineWidth }
    var fillValue = s.fillEnabled ? fill(s.color) : ""

    if (tool === "pen" || tool === "eraser") {
        return s.points.length > 0 ? withStyle(tool, style, { points: s.points.slice() }) : null
    }
    if (tool === "line" || tool === "arrow") {
        if (Math.hypot(dx, dy) < 3) return null
        var segment = { x1: s.startX, y1: s.startY, x2: s.currentX, y2: s.currentY }
        if (tool === "arrow") segment.label = ""
        return withStyle(tool, style, segment)
    }
    if (tool === "rect" || tool === "round_rect") {
        if (dx < 3 || dy < 3) return null
        var box = { x: x, y: y, w: dx, h: dy, fill: fillValue, text: "" }
        if (tool === "round_rect") box.r = 8
        return withStyle(tool, style, box)
    }
    if (tool === "circle") {
        if (dx / 2 < 2 || dy / 2 < 2) return null
        return withStyle(tool, style, {
            cx: (s.startX + s.currentX) / 2,
            cy: (s.startY + s.currentY) / 2,
            rx: dx / 2,
            ry: dy / 2,
            fill: fillValue,
            text: ""
        })
    }
    var block = FLOW_BLOCKS[tool]
    if (!block) return null
    return withStyle(tool, style, {
        x: x,
        y: y,
        w: Math.max(block.minW, dx),
        h: Math.max(block.minH, dy),
        fill: fill(s.color),
        text: block.text
    })
}

// Her öğe tür, renk ve kalınlıkla başlar; şekle özgü alanlar arkasından gelir.
function withStyle(type, style, shape) {
    var item = { type: type, color: style.color, width: style.width }
    for (var key in shape) {
        item[key] = shape[key]
    }
    return item
}
