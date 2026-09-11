# Builds dist\tunemeta.exe -- a single portable executable, no installer needed.
# Run from a Windows machine with `pip install -e ".[gui,build]"` done first.
$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $PSScriptRoot
Set-Location $RootDir

pyinstaller `
  --onefile `
  --windowed `
  --name tunemeta `
  --noconfirm `
  --distpath dist `
  --workpath build `
  --specpath build `
  src/tunemeta/gui.py

Write-Host "Built dist\tunemeta.exe"
