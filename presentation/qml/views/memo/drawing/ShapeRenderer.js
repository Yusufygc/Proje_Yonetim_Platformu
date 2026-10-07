.pragma library

// Tuval şekillerini 2B bağlama çizen saf fonksiyonlar; QML duruma erişmez.
// `palette`: { background, pen, text } tema renkleri.

function renderItem(ctx, item, palette) {
    if (!item) return

    // 1. Serbest Çizgi veya Silgi (Points dizisi)
    if (item.points && (item.type === "pen" || item.type === "eraser" || !item.type)) {
        if (item.points.length === 1) {
            ctx.fillStyle = item.type === "eraser" ? palette.background : (item.color || palette.pen)
            ctx.beginPath()
            ctx.arc(item.points[0].x, item.points[0].y, (item.width || 3) / 2, 0, 2 * Math.PI)
            ctx.fill()
        } else if (item.points.length > 1) {
            ctx.strokeStyle = item.type === "eraser" ? palette.background : (item.color || palette.pen)
            ctx.lineWidth = item.width || 3
            ctx.lineCap = "round"
            ctx.lineJoin = "round"
            ctx.beginPath()
            ctx.moveTo(item.points[0].x, item.points[0].y)
            for (var j = 1; j < item.points.length; j++) {
                ctx.lineTo(item.points[j].x, item.points[j].y)
            }
            ctx.stroke()
        }
        return
    }

    // 2. Düz Çizgi
    if (item.type === "line") {
        ctx.strokeStyle = item.color
        ctx.lineWidth = item.width || 3
        ctx.lineCap = "round"
        ctx.beginPath()
        ctx.moveTo(item.x1, item.y1)
        ctx.lineTo(item.x2, item.y2)
        ctx.stroke()
        return
    }

    // 3. Ok
    if (item.type === "arrow") {
        drawArrow(ctx, item.x1, item.y1, item.x2, item.y2, item.color, item.width || 3, item.label || "")
        return
    }

    // 4. Dikdörtgen
    if (item.type === "rect") {
        if (item.fill && item.fill !== "") {
            ctx.fillStyle = item.fill
            ctx.fillRect(item.x, item.y, item.w, item.h)
        }
        ctx.strokeStyle = item.color
        ctx.lineWidth = item.width || 3
        ctx.strokeRect(item.x, item.y, item.w, item.h)
        if (item.text) drawCenteredText(ctx, item.text, item.x + item.w / 2, item.y + item.h / 2, item.color, palette.text)
        return
    }

    // 5. Oval / Yuvarlak Kutu
    if (item.type === "round_rect") {
        drawRoundRect(ctx, item.x, item.y, item.w, item.h, item.r || 8, item.color, item.width || 3, item.fill)
        if (item.text) drawCenteredText(ctx, item.text, item.x + item.w / 2, item.y + item.h / 2, item.color, palette.text)
        return
    }

    // 6. Daire / Elips
    if (item.type === "circle") {
        drawEllipse(ctx, item.cx, item.cy, item.rx, item.ry, item.color, item.width || 3, item.fill)
        if (item.text) drawCenteredText(ctx, item.text, item.cx, item.cy, item.color, palette.text)
        return
    }

    // 7. Akış Şeması: Başla / Bitir (Kapsül)
    if (item.type === "flow_start") {
        var r = Math.min(item.w, item.h) / 2
        drawRoundRect(ctx, item.x, item.y, item.w, item.h, r, item.color, item.width || 2, item.fill)
        drawCenteredText(ctx, item.text || "Başla", item.x + item.w / 2, item.y + item.h / 2, item.color, palette.text)
        return
    }

    // 8. Akış Şeması: İşlem (Dikdörtgen)
    if (item.type === "flow_process") {
        if (item.fill && item.fill !== "") {
            ctx.fillStyle = item.fill
            ctx.fillRect(item.x, item.y, item.w, item.h)
        }
        ctx.strokeStyle = item.color
        ctx.lineWidth = item.width || 2
        ctx.strokeRect(item.x, item.y, item.w, item.h)
        drawCenteredText(ctx, item.text || "İşlem", item.x + item.w / 2, item.y + item.h / 2, item.color, palette.text)
        return
    }

    // 9. Akış Şeması: Karar / Koşul (Baklava / Diamond)
    if (item.type === "flow_decision") {
        ctx.beginPath()
        ctx.moveTo(item.x + item.w / 2, item.y)
        ctx.lineTo(item.x + item.w, item.y + item.h / 2)
        ctx.lineTo(item.x + item.w / 2, item.y + item.h)
        ctx.lineTo(item.x, item.y + item.h / 2)
        ctx.closePath()
        if (item.fill && item.fill !== "") {
            ctx.fillStyle = item.fill
            ctx.fill()
        }
        ctx.strokeStyle = item.color
        ctx.lineWidth = item.width || 2
        ctx.stroke()
        drawCenteredText(ctx, item.text || "Koşul ?", item.x + item.w / 2, item.y + item.h / 2, item.color, palette.text)
        return
    }

    // 10. Akış Şeması: Girdi / Çıktı (Paralelkenar)
    if (item.type === "flow_io") {
        var skew = Math.min(18, item.w * 0.18)
        ctx.beginPath()
        ctx.moveTo(item.x + skew, item.y)
        ctx.lineTo(item.x + item.w, item.y)
        ctx.lineTo(item.x + item.w - skew, item.y + item.h)
        ctx.lineTo(item.x, item.y + item.h)
        ctx.closePath()
        if (item.fill && item.fill !== "") {
            ctx.fillStyle = item.fill
            ctx.fill()
        }
        ctx.strokeStyle = item.color
        ctx.lineWidth = item.width || 2
        ctx.stroke()
        drawCenteredText(ctx, item.text || "Girdi/Çıktı", item.x + item.w / 2, item.y + item.h / 2, item.color, palette.text)
        return
    }
}

// Çizim sürerken gösterilen canlı önizleme. `s`: araç, renk ve sürükleme koordinatları.
function renderLivePreview(ctx, s, palette) {
    var col = s.color
    var lw = s.lineWidth
    var fill = s.fillEnabled ? fillColor(col, palette.pen) : ""
    var box = normalizedBox(s)

    if (s.tool === "pen" || s.tool === "eraser") {
        previewStroke(ctx, s.points, col, lw)
    } else if (s.tool === "line") {
        ctx.strokeStyle = col
        ctx.lineWidth = lw
        ctx.lineCap = "round"
        ctx.beginPath()
        ctx.moveTo(s.startX, s.startY)
        ctx.lineTo(s.currentX, s.currentY)
        ctx.stroke()
    } else if (s.tool === "arrow") {
        drawArrow(ctx, s.startX, s.startY, s.currentX, s.currentY, col, lw, "")
    } else if (s.tool === "rect") {
        if (s.fillEnabled) {
            ctx.fillStyle = fill
            ctx.fillRect(box.x, box.y, box.w, box.h)
        }
        ctx.strokeStyle = col
        ctx.lineWidth = lw
        ctx.strokeRect(box.x, box.y, box.w, box.h)
    } else if (s.tool === "round_rect") {
        drawRoundRect(ctx, box.x, box.y, box.w, box.h, 8, col, lw, fill)
    } else if (s.tool === "circle") {
        drawEllipse(ctx, (s.startX + s.currentX) / 2, (s.startY + s.currentY) / 2, box.w / 2, box.h / 2, col, lw, fill)
    } else if (s.tool.indexOf("flow_") === 0) {
        previewFlowBlock(ctx, s, palette)
    }
}

function normalizedBox(s) {
    return {
        x: Math.min(s.startX, s.currentX),
        y: Math.min(s.startY, s.currentY),
        w: Math.abs(s.currentX - s.startX),
        h: Math.abs(s.currentY - s.startY)
    }
}

function previewStroke(ctx, points, color, width) {
    if (points.length <= 1) return
    ctx.strokeStyle = color
    ctx.lineWidth = width
    ctx.lineCap = "round"
    ctx.lineJoin = "round"
    ctx.beginPath()
    ctx.moveTo(points[0].x, points[0].y)
    for (var k = 1; k < points.length; k++) {
        ctx.lineTo(points[k].x, points[k].y)
    }
    ctx.stroke()
}

// Akış şeması blokları, bırakıldığındaki asgari boyutlarla önizlenir.
var FLOW_MIN_SIZE = {
    flow_start: [40, 26],
    flow_process: [50, 30],
    flow_decision: [50, 36],
    flow_io: [50, 30]
}

function previewFlowBlock(ctx, s, palette) {
    var min = FLOW_MIN_SIZE[s.tool]
    var box = normalizedBox(s)
    var x = box.x
    var y = box.y
    var w = Math.max(min[0], box.w)
    var h = Math.max(min[1], box.h)
    var fill = fillColor(s.color, palette.pen)

    if (s.tool === "flow_start") {
        drawRoundRect(ctx, x, y, w, h, Math.min(w, h) / 2, s.color, s.lineWidth, fill)
        return
    }
    if (s.tool === "flow_process") {
        ctx.fillStyle = fill
        ctx.fillRect(x, y, w, h)
        ctx.strokeStyle = s.color
        ctx.lineWidth = s.lineWidth
        ctx.strokeRect(x, y, w, h)
        return
    }
    ctx.beginPath()
    if (s.tool === "flow_decision") {
        ctx.moveTo(x + w / 2, y)
        ctx.lineTo(x + w, y + h / 2)
        ctx.lineTo(x + w / 2, y + h)
        ctx.lineTo(x, y + h / 2)
    } else {
        var skew = Math.min(18, w * 0.18)
        ctx.moveTo(x + skew, y)
        ctx.lineTo(x + w, y)
        ctx.lineTo(x + w - skew, y + h)
        ctx.lineTo(x, y + h)
    }
    ctx.closePath()
    ctx.fillStyle = fill
    ctx.fill()
    ctx.strokeStyle = s.color
    ctx.lineWidth = s.lineWidth
    ctx.stroke()
}

// Dolgu rengi: çizgi renginin yarı saydam hâli.
function fillColor(hexColor, fallback) {
    var c = Qt.color(hexColor || fallback)
    return Qt.rgba(c.r, c.g, c.b, 0.18)
}

function drawArrow(ctx, x1, y1, x2, y2, color, width, label) {
    ctx.strokeStyle = color
    ctx.lineWidth = width
    ctx.lineCap = "round"
    ctx.lineJoin = "round"
    ctx.beginPath()
    ctx.moveTo(x1, y1)
    ctx.lineTo(x2, y2)
    ctx.stroke()

    var angle = Math.atan2(y2 - y1, x2 - x1)
    var headLen = Math.max(12, width * 3.5)
    ctx.fillStyle = color
    ctx.beginPath()
    ctx.moveTo(x2, y2)
    ctx.lineTo(x2 - headLen * Math.cos(angle - Math.PI / 7), y2 - headLen * Math.sin(angle - Math.PI / 7))
    ctx.lineTo(x2 - headLen * Math.cos(angle + Math.PI / 7), y2 - headLen * Math.sin(angle + Math.PI / 7))
    ctx.closePath()
    ctx.fill()

    if (label && label.length > 0) {
        var mx = (x1 + x2) / 2
        var my = (y1 + y2) / 2
        ctx.save()
        ctx.font = "bold 11px sans-serif"
        ctx.fillStyle = color
        ctx.textAlign = "center"
        ctx.textBaseline = "bottom"
        ctx.fillText(label, mx, my - 4)
        ctx.restore()
    }
}

function drawRoundRect(ctx, x, y, w, h, r, color, width, fill) {
    if (w < 2 * r) r = w / 2
    if (h < 2 * r) r = h / 2
    ctx.beginPath()
    ctx.moveTo(x + r, y)
    ctx.arcTo(x + w, y, x + w, y + h, r)
    ctx.arcTo(x + w, y + h, x, y + h, r)
    ctx.arcTo(x, y + h, x, y, r)
    ctx.arcTo(x, y, x + w, y, r)
    ctx.closePath()
    if (fill && fill !== "") {
        ctx.fillStyle = fill
        ctx.fill()
    }
    ctx.strokeStyle = color
    ctx.lineWidth = width
    ctx.stroke()
}

function drawEllipse(ctx, cx, cy, rx, ry, color, width, fill) {
    if (rx <= 0.5 || ry <= 0.5) return
    ctx.save()
    ctx.beginPath()
    ctx.translate(cx, cy)
    ctx.scale(rx, ry)
    ctx.arc(0, 0, 1, 0, 2 * Math.PI, false)
    ctx.restore()
    if (fill && fill !== "") {
        ctx.fillStyle = fill
        ctx.fill()
    }
    ctx.strokeStyle = color
    ctx.lineWidth = width
    ctx.stroke()
}

function drawCenteredText(ctx, text, cx, cy, color, defaultColor) {
    if (!text || text.trim().length === 0) return
    ctx.save()
    ctx.font = "bold 12px sans-serif"
    ctx.fillStyle = color || defaultColor
    ctx.textAlign = "center"
    ctx.textBaseline = "middle"

    var lines = text.split("\n")
    var lineHeight = 15
    var totalH = lines.length * lineHeight
    var sy = cy - (totalH / 2) + (lineHeight / 2)

    for (var i = 0; i < lines.length; i++) {
        ctx.fillText(lines[i], cx, sy + (i * lineHeight))
    }
    ctx.restore()
}
