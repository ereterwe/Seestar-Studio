param([switch]$SkipTests)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
$version = & $python -c 'from seestar_studio import __version__; print(__version__)'
if ($LASTEXITCODE -ne 0) { throw 'Version lookup failed' }
$outputRoot = Join-Path $PSScriptRoot "dist\$version"
$runningTarget = Join-Path $outputRoot 'SeestarStudio\SeestarStudio.exe'
if (Get-Process SeestarStudio -ErrorAction SilentlyContinue | Where-Object { $_.Path -eq $runningTarget }) { throw 'This build version is running. Close it explicitly before replacing it.' }
& $python -m tools.build_metadata
if ($LASTEXITCODE -ne 0) { throw 'Build metadata failed' }
if (-not $SkipTests) {
    & $python -m pytest -q
    if ($LASTEXITCODE -ne 0) { throw 'Tests failed' }
}
& $python -m PyInstaller --noconfirm --distpath $outputRoot SeestarStudio.spec
if ($LASTEXITCODE -ne 0) { throw 'Build failed' }
& $python -m tools.license_audit
if ($LASTEXITCODE -ne 0) { throw 'Dependency inventory failed' }
& $python -m tools.package_release
if ($LASTEXITCODE -ne 0) { throw 'Packaging failed' }
Write-Host "Start: dist\$version\SeestarStudio\SeestarStudio.exe"
