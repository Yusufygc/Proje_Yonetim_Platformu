param(
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Spec = Join-Path $Root "packaging\proje_takip_platformu.spec"

if ($Clean) {
    Remove-Item -LiteralPath (Join-Path $Root "build") -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath (Join-Path $Root "dist") -Recurse -Force -ErrorAction SilentlyContinue
}

uv run pyinstaller --noconfirm --clean $Spec
