param([string]$Version = '2.2.0.dev1')
$ErrorActionPreference = 'Stop'
$workspace = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$testDirectory = [IO.Path]::GetFullPath((Join-Path $workspace "reports\installer-qa-$Version"))
if (-not $testDirectory.StartsWith($workspace + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Unsafe QA target' }
$registration = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\{A8B6B872-6710-44A3-94A6-1C953E3B8D87}_is1'
$shortcut = Join-Path ([Environment]::GetFolderPath('Programs')) 'Seestar Studio.lnk'
if ((Test-Path -LiteralPath $registration) -or (Test-Path -LiteralPath $testDirectory) -or (Test-Path -LiteralPath $shortcut)) {
    throw 'Existing installation, shortcut or QA folder detected; nothing changed'
}
$profile = Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'SeestarStudio\Seestar Studio'
function Get-ProfileState {
    $state = @{}
    # Never read key files. Hash only configuration and session database files.
    foreach ($name in @('settings.json', 'history.sqlite3', 'authentication\authentication.json')) {
        $file = Join-Path $profile $name
        $state[$name] = if (Test-Path -LiteralPath $file) { (Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash } else { 'absent' }
    }
    return ($state | ConvertTo-Json -Compress)
}
$before = Get-ProfileState
$installer = Join-Path $workspace "release\SeestarStudio-$Version-setup-win64.exe"
$arguments = "/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /CURRENTUSER /DIR=`"$testDirectory`""
$first = Start-Process -FilePath $installer -ArgumentList $arguments -WindowStyle Hidden -Wait -PassThru
if ($first.ExitCode -ne 0) { throw "Install exit $($first.ExitCode)" }
$installedExe = Join-Path $testDirectory 'SeestarStudio.exe'
$expected = (Get-FileHash -LiteralPath (Join-Path $workspace "dist\$Version\SeestarStudio\SeestarStudio.exe")).Hash
$matches = (Get-FileHash -LiteralPath $installedExe).Hash -eq $expected
$shortcutCreated = Test-Path -LiteralPath $shortcut
$second = Start-Process -FilePath $installer -ArgumentList $arguments -WindowStyle Hidden -Wait -PassThru
if ($second.ExitCode -ne 0) { throw "Upgrade exit $($second.ExitCode)" }
$uninstaller = [IO.Path]::GetFullPath((Join-Path $testDirectory 'unins000.exe'))
if (-not $uninstaller.StartsWith($testDirectory + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Unsafe uninstaller target' }
$remove = Start-Process -FilePath $uninstaller -ArgumentList '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART' -WindowStyle Hidden -Wait -PassThru
$report = [ordered]@{
    test_type = 'local Windows install/reinstall/uninstall; not external clean PC'
    install_exit = $first.ExitCode; reinstall_exit = $second.ExitCode; uninstall_exit = $remove.ExitCode
    installed_exe_matches = $matches; start_menu_created = $shortcutCreated
    program_removed = -not (Test-Path -LiteralPath $installedExe)
    start_menu_removed = -not (Test-Path -LiteralPath $shortcut)
    registration_removed = -not (Test-Path -LiteralPath $registration)
    existing_profile_unchanged = (Get-ProfileState) -eq $before
    application_started = $false
}
$report | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $workspace "reports\installer-qa-$Version.json") -Encoding UTF8
$report | ConvertTo-Json
if ($remove.ExitCode -ne 0 -or -not $matches -or -not $report.program_removed -or -not $report.existing_profile_unchanged) { exit 1 }
