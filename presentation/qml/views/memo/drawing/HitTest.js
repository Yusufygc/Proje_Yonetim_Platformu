.pragma library

// Çift tıklanan noktadaki en üstteki öğenin indeksini bulur (yoksa -1).
function findItemAt(items, x, y) {
    for (var i = items.length - 1; i >= 0; i--) {
        var it = items[i]
        if (!it) continue
        if (it.type === "flow_start" || it.type === "flow_process" || it.type === "flow_decision" || it.type === "flow_io" || it.type === "rect" || it.type === "round_rect") {
            if (x >= it.x && x <= it.x + it.w && y >= it.y && y <= it.y + it.h) {
                return i
            }
        } else if (it.type === "circle") {
            var dx = (x - it.cx) / (it.rx || 1)
            var dy = (y - it.cy) / (it.ry || 1)
            if (dx * dx + dy * dy <= 1) {
                return i
            }
        } else if (it.type === "arrow" || it.type === "line") {
            var dist = distanceToSegment(x, y, it.x1, it.y1, it.x2, it.y2)
            if (dist <= 12) {
                return i
            }
        }
    }
    return -1
}

function distanceToSegment(px, py, x1, y1, x2, y2) {
    var l2 = (x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1)
    if (l2 === 0) return Math.hypot(px - x1, py - y1)
    var t = ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / l2
    t = Math.max(0, Math.min(1, t))
    return Math.hypot(px - (x1 + t * (x2 - x1)), py - (y1 + t * (y2 - y1)))
}
