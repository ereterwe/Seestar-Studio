param([string]$Compiler = '', [string]$SourceRoot = '', [string]$OutputDirectory = '')
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not $Compiler) {
    $Compiler = Join-Path $PSScriptRoot '.build-tools\innosetup\ISCC.exe'
    if (-not (Test-Path -LiteralPath $Compiler)) {
        $Compiler = (Get-Command ISCC.exe -ErrorAction Stop).Source
    }
}
$version = & '.\.venv\Scripts\python.exe' -c 'from telescope_desk import __version__; print(__version__)'
if ($LASTEXITCODE -ne 0) { throw 'Version lookup failed' }
if (-not $SourceRoot) { $SourceRoot = Join-Path $PSScriptRoot "dist\$version\TelescopeDesk" }
$SourceRoot = [IO.Path]::GetFullPath($SourceRoot)
if (-not (Test-Path -LiteralPath (Join-Path $sourceRoot 'TelescopeDesk.exe'))) { throw 'Run build.ps1 first' }
$compilerArguments = @("/DAppVersion=$version", "/DSourceRoot=$sourceRoot")
if ($OutputDirectory) { $compilerArguments += "/O$([IO.Path]::GetFullPath($OutputDirectory))" }
& $Compiler @compilerArguments 'installer\TelescopeDesk.iss'
if ($LASTEXITCODE -ne 0) { throw 'Installer compilation failed' }
Write-Host "Installer completed for $version"
