param(
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Spec = Join-Path $Root "packaging\proje_takip_platformu_dir.spec"
$Iss = Join-Path $Root "installer\windows.iss"
$ISCC = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

# Eğer temizlik istenirse
if ($Clean) {
    Write-Host "Temizlik yapılıyor..." -ForegroundColor Yellow
    Remove-Item -LiteralPath (Join-Path $Root "build") -Recurse -Force -ErrorAction SilentlyContinue
    # dist/ altındaki ProjeTakipPlatformu klasörünü ve installer klasörünü siliyoruz
    Remove-Item -LiteralPath (Join-Path $Root "dist\ProjeTakipPlatformu") -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath (Join-Path $Root "dist\installer") -Recurse -Force -ErrorAction SilentlyContinue
}

# 1. PyInstaller ile Klasör Modunda Derleme Yap
Write-Host "1. PyInstaller ile derleme yapılıyor (Klasör Modu)..." -ForegroundColor Cyan
uv run pyinstaller --noconfirm --clean $Spec

# 2. Inno Setup ile Kurulum Sihirbazı Oluştur
if (Test-Path $ISCC) {
    Write-Host "2. Inno Setup ile Kurulum Sihirbazı (setup.exe) oluşturuluyor..." -ForegroundColor Cyan
    & $ISCC $Iss
    Write-Host "Kurulum Sihirbazı başarıyla oluşturuldu! Çıktı: dist/installer/" -ForegroundColor Green
} else {
    Write-Error "Inno Setup Compiler (ISCC.exe) bulunamadı! Lütfen kuruluma dikkat edin veya yolu kontrol edin."
}
