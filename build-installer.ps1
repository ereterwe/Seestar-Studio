param([string]$Compiler = '')
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not $Compiler) {
    $Compiler = Join-Path $PSScriptRoot '.build-tools\innosetup\ISCC.exe'
    if (-not (Test-Path -LiteralPath $Compiler)) {
        $Compiler = (Get-Command ISCC.exe -ErrorAction Stop).Source
    }
}
$version = & '.\.venv\Scripts\python.exe' -c 'from seestar_studio import __version__; print(__version__)'
if ($LASTEXITCODE -ne 0) { throw 'Version lookup failed' }
$sourceRoot = Join-Path $PSScriptRoot "dist\$version\SeestarStudio"
if (-not (Test-Path -LiteralPath (Join-Path $sourceRoot 'SeestarStudio.exe'))) { throw 'Run build.ps1 first' }
& $Compiler "/DAppVersion=$version" "/DSourceRoot=$sourceRoot" 'installer\SeestarStudio.iss'
if ($LASTEXITCODE -ne 0) { throw 'Installer compilation failed' }
Write-Host "Installer: release\SeestarStudio-$version-setup-win64.exe"
