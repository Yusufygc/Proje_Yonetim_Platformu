.pragma library

// Tuval içeriğinin JSON gösterimi. Arka plan görseli yoksa eski biçim (yalnızca öğe dizisi) yazılır,
// böylece daha önce kaydedilmiş notlar ve eski sürümler aynı veriyi okuyabilir.

function serialize(items, backgroundImage) {
    if (backgroundImage !== "") {
        return JSON.stringify({ version: 2, backgroundImage: backgroundImage, items: items })
    }
    return JSON.stringify(items)
}

// Geçersiz veya boş girdide boş tuval döner. `penColor`: türü olmayan eski çizgilerin rengi.
function parse(jsonStr, penColor) {
    var empty = { items: [], backgroundImage: "" }
    if (!jsonStr || jsonStr.trim().length === 0) return empty
    try {
        var parsed = JSON.parse(jsonStr)
        if (Array.isArray(parsed)) {
            return { items: parsed.map(function(item) { return upgradeLegacyItem(item, penColor) }), backgroundImage: "" }
        }
        if (parsed && parsed.items && Array.isArray(parsed.items)) {
            return { items: parsed.items, backgroundImage: parsed.backgroundImage || "" }
        }
    } catch (e) {
        return empty
    }
    return empty
}

// İlk sürümde öğelerin `type` alanı yoktu; yalnızca serbest çizgi vardı.
function upgradeLegacyItem(item, penColor) {
    if (item.type) return item
    return { type: "pen", color: item.color || penColor, width: item.width || 3, points: item.points || [] }
}

// Geri al/yinele yığınındaki bir anlık görüntü; arka plan görselini de içerir.
function snapshot(items, backgroundImage) {
    return JSON.stringify({ backgroundImage: backgroundImage, items: items })
}

// Eski kayıtlar yalnızca öğe dizisiydi; arka plan görseli o zaman yoktu.
function restoreSnapshot(raw) {
    var parsed = JSON.parse(raw)
    if (Array.isArray(parsed)) return { items: parsed, backgroundImage: "" }
    if (!parsed) return { items: [], backgroundImage: "" }
    return { items: parsed.items || [], backgroundImage: parsed.backgroundImage || "" }
}
