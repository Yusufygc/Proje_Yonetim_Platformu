import urllib.request
import os
import zipfile
import io
from pathlib import Path

icons_dir = Path("resources/icons")
fonts_dir = Path("resources/fonts")
icons_dir.mkdir(parents=True, exist_ok=True)
fonts_dir.mkdir(parents=True, exist_ok=True)

# Temizleme: Fonts dizinindeki her şeyi temizle (temiz bir başlangıç için)
for font_file in fonts_dir.glob("*.ttf"):
    try:
        os.remove(font_file)
        print(f"Deleted old font: {font_file.name}")
    except Exception as e:
        print(f"Failed to delete old font {font_file.name}: {e}")

# İkonları indir (Güncel Lucide isimleri ve URL'leri ile)
icons = {
    "house": "https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/house.svg",
    "folder": "https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/folder.svg",
    "lightbulb": "https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/lightbulb.svg",
    "square-check": "https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/square-check.svg",
    "settings": "https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/settings.svg",
    "search": "https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/search.svg",
}

for name, url in icons.items():
    print(f"Downloading icon: {name}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            (icons_dir / f"{name}.svg").write_bytes(response.read())
        print(f"Successfully downloaded icon: {name}")
    except Exception as e:
        print(f"Failed to download icon {name}: {e}")

# Inter Fontunu (Yalnızca gerekli statik dosyaları) İndir ve Çıkar
font_zip_url = "https://github.com/rsms/inter/releases/download/v4.0/Inter-4.0.zip"
print("Downloading Inter font zip...")
try:
    req = urllib.request.Request(font_zip_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        zip_data = response.read()
    
    print("Extracting select static Inter font files...")
    # Sadece bu 3 dosyayı çıkaracağız (hafiflik ve stabilite için)
    allowed_fonts = {"Inter-Regular.ttf", "Inter-Bold.ttf", "Inter-Medium.ttf"}
    
    with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
        for member in z.namelist():
            filename = Path(member).name
            if member.startswith("extras/ttf/") and filename in allowed_fonts:
                (fonts_dir / filename).write_bytes(z.read(member))
                print(f"Extracted static font: {filename}")
except Exception as e:
    print(f"Failed to download or extract static Inter font: {e}")

print("Done!")
