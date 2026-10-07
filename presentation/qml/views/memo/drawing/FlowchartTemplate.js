.pragma library

// Hazır "sayı pozitif mi?" akış şeması. `fill`: çizgi renginden dolgu rengi üreten fonksiyon.
function createItems(isDark, fill) {
    var startCol = "#10B981"  // Yeşil
    var procCol = "#3B82F6"   // Mavi
    var decCol = "#F59E0B"    // Sarı / Turuncu
    var arrowCol = isDark ? "#A1A1AA" : "#4B5563"

    return [
        // 1. Başla
        { type: "flow_start", x: 120, y: 30, w: 120, h: 44, color: startCol, width: 2, fill: fill(startCol), text: "Başla" },
        // Ok
        { type: "arrow", x1: 180, y1: 74, x2: 180, y2: 110, color: arrowCol, width: 2, label: "" },
        // 2. Girdi
        { type: "flow_io", x: 100, y: 110, w: 160, h: 46, color: procCol, width: 2, fill: fill(procCol), text: "Sayıyı Oku (N)" },
        // Ok
        { type: "arrow", x1: 180, y1: 156, x2: 180, y2: 195, color: arrowCol, width: 2, label: "" },
        // 3. Karar
        { type: "flow_decision", x: 100, y: 195, w: 160, h: 70, color: decCol, width: 2, fill: fill(decCol), text: "N > 0 ?" },
        // Ok Sağa (Evet)
        { type: "arrow", x1: 260, y1: 230, x2: 340, y2: 230, color: arrowCol, width: 2, label: "Evet" },
        // 4. İşlem (Pozitif)
        { type: "flow_process", x: 340, y: 205, w: 150, h: 50, color: procCol, width: 2, fill: fill(procCol), text: "'Pozitif' Yaz" },
        // Ok Aşağı (Hayır)
        { type: "arrow", x1: 180, y1: 265, x2: 180, y2: 310, color: arrowCol, width: 2, label: "Hayır" },
        // 5. İşlem (Negatif veya 0)
        { type: "flow_process", x: 95, y: 310, w: 170, h: 50, color: procCol, width: 2, fill: fill(procCol), text: "'Negatif / 0' Yaz" },
        // Oklar Bitir'e
        { type: "arrow", x1: 180, y1: 360, x2: 180, y2: 400, color: arrowCol, width: 2, label: "" },
        { type: "arrow", x1: 415, y1: 255, x2: 415, y2: 422, color: arrowCol, width: 2, label: "" },
        { type: "arrow", x1: 415, y1: 422, x2: 240, y2: 422, color: arrowCol, width: 2, label: "" },
        // 6. Bitir
        { type: "flow_start", x: 120, y: 400, w: 120, h: 44, color: "#EF4444", width: 2, fill: fill("#EF4444"), text: "Bitir" }
    ]
}
