param([ValidateSet('Install','Cleanup')][string]$Stage='Install',
      [string]$SourceDirectory='', [string]$InstallerPath='',
      [ValidatePattern('^[a-z0-9-]{0,50}$')][string]$CaseName='')
$ErrorActionPreference='Stop'
$workspace=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
Set-Location -LiteralPath $workspace
$version=& '.\.venv\Scripts\python.exe' -c 'from telescope_desk import __version__; print(__version__)'
if ($LASTEXITCODE -ne 0) { throw 'Version lookup failed' }
$suffix=if ($CaseName) { '-'+$CaseName } else { '' }
$testDirectory=[IO.Path]::GetFullPath((Join-Path $workspace "reports\beta-installed-$version$suffix"))
if (-not $testDirectory.StartsWith($workspace+'\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Unsafe test directory' }
$stateFile=Join-Path $workspace "reports\beta-installer-state$suffix.json"
$registration='HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\{BF344EF3-C3B3-4514-8B99-57CA7F157280}_is1'
$shortcut=Join-Path ([Environment]::GetFolderPath('Programs')) 'Telescope Desk.lnk'
$desktopShortcut=Join-Path ([Environment]::GetFolderPath('Desktop')) 'Telescope Desk.lnk'
function Get-ProfileState {
    $state=@{}
    foreach ($kind in @('LocalApplicationData','ApplicationData')) {
      foreach ($profileName in @('TelescopeDesk\Telescope Desk','SeestarStudio\Seestar Studio')) {
        $base=Join-Path ([Environment]::GetFolderPath($kind)) $profileName
        foreach ($name in @('settings.json','history.sqlite3','authentication\authentication.json')) {
            $file=Join-Path $base $name
            $state["$kind/$profileName/$name"]=if (Test-Path -LiteralPath $file) {(Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash} else {'absent'}
        }
      }
    }
    return $state
}
if ($Stage -eq 'Install') {
    if ((Test-Path -LiteralPath $registration) -or (Test-Path -LiteralPath $testDirectory) -or (Test-Path -LiteralPath $shortcut) -or (Test-Path -LiteralPath $desktopShortcut)) { throw 'Existing installation or shortcut detected; nothing changed' }
    if (Get-Process TelescopeDesk -ErrorAction SilentlyContinue) { throw 'An application instance is running; nothing changed' }
    $before=Get-ProfileState
    $installer=if ($InstallerPath) { [IO.Path]::GetFullPath($InstallerPath) } else { Join-Path $workspace "release\TelescopeDesk-$version-setup-win64.exe" }
    $arguments="/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /CURRENTUSER /TASKS=desktopicon /DIR=`"$testDirectory`""
    $first=Start-Process -FilePath $installer -ArgumentList $arguments -WindowStyle Hidden -Wait -PassThru
    if ($first.ExitCode -ne 0) { throw "Install exit $($first.ExitCode)" }
    $installedExe=Join-Path $testDirectory 'TelescopeDesk.exe'
    $portableDirectory=if ($SourceDirectory) { [IO.Path]::GetFullPath($SourceDirectory) } else { Join-Path $workspace "dist\$version\TelescopeDesk" }
    $matches=(Get-FileHash -LiteralPath $installedExe).Hash -eq (Get-FileHash -LiteralPath (Join-Path $portableDirectory 'TelescopeDesk.exe')).Hash
    $second=Start-Process -FilePath $installer -ArgumentList $arguments -WindowStyle Hidden -Wait -PassThru
    if ($second.ExitCode -ne 0) { throw "Reinstall exit $($second.ExitCode)" }
    $payload=Get-ChildItem -LiteralPath $portableDirectory -File -Recurse
    $mismatches=@(foreach ($file in $payload) {
        $relative=$file.FullName.Substring($portableDirectory.Length).TrimStart('\')
        $installedFile=Join-Path $testDirectory $relative
        if (-not (Test-Path -LiteralPath $installedFile)) { $relative }
        elseif ((Get-FileHash -LiteralPath $file.FullName).Hash -ne (Get-FileHash -LiteralPath $installedFile).Hash) { $relative }
    })
    $shell=New-Object -ComObject WScript.Shell
    $startLink=$shell.CreateShortcut($shortcut)
    $desktopLink=$shell.CreateShortcut($desktopShortcut)
    $record=Get-ItemProperty -LiteralPath $registration
    $state=@{version=$version;directory=$testDirectory;profile_before=$before;install_exit=$first.ExitCode;reinstall_exit=$second.ExitCode;installed_exe_matches=$matches;start_menu_created=(Test-Path -LiteralPath $shortcut);desktop_created=(Test-Path -LiteralPath $desktopShortcut);start_menu_icon_matches=$startLink.IconLocation.StartsWith($installedExe,[StringComparison]::OrdinalIgnoreCase);desktop_icon_matches=$desktopLink.IconLocation.StartsWith($installedExe,[StringComparison]::OrdinalIgnoreCase);uninstall_icon_matches=$record.DisplayIcon.StartsWith($installedExe,[StringComparison]::OrdinalIgnoreCase);test_type='real local production installer; no clean external PC'}
    $state | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $stateFile -Encoding utf8
    $state.payload_files_checked=$payload.Count
    $state.payload_mismatches=$mismatches.Count
    $state | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $stateFile -Encoding utf8
    if ($mismatches.Count -ne 0 -or -not $matches -or -not $state.start_menu_created -or -not $state.desktop_created -or -not $state.start_menu_icon_matches -or -not $state.desktop_icon_matches -or -not $state.uninstall_icon_matches) { throw 'Installed payload/shortcut verification failed; QA state preserved for cleanup' }
    Write-Output 'Installed/reinstalled in isolated QA directory. Ready for visual inspection.'
} else {
    $state=Get-Content -LiteralPath $stateFile -Raw | ConvertFrom-Json -AsHashtable
    if ($state.directory -ne $testDirectory -or $state.version -ne $version) { throw 'QA state does not match target' }
    $record=Get-ItemProperty -LiteralPath $registration
    if ([IO.Path]::GetFullPath($record.InstallLocation).TrimEnd('\') -ne $testDirectory.TrimEnd('\')) { throw 'Different installed location; no uninstall' }
    if (Get-Process TelescopeDesk -ErrorAction SilentlyContinue | Where-Object {$_.Path -eq (Join-Path $testDirectory 'TelescopeDesk.exe')}) { throw 'QA application still running' }
    $uninstaller=[IO.Path]::GetFullPath((Join-Path $testDirectory 'unins000.exe'))
    if (-not $uninstaller.StartsWith($testDirectory+'\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Unsafe uninstaller target' }
    $remove=Start-Process -FilePath $uninstaller -ArgumentList '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART' -WindowStyle Hidden -Wait -PassThru
    $after=Get-ProfileState
    $state.profile_unchanged=@($state.profile_before.Keys | Where-Object {$state.profile_before[$_] -ne $after[$_]}).Count -eq 0
    $state.uninstall_exit=$remove.ExitCode
    $state.program_removed=-not (Test-Path -LiteralPath (Join-Path $testDirectory 'TelescopeDesk.exe'))
    $state.shortcuts_removed=(-not (Test-Path -LiteralPath $shortcut)) -and (-not (Test-Path -LiteralPath $desktopShortcut))
    $state.registration_removed=-not (Test-Path -LiteralPath $registration)
    $state.Remove('profile_before');$state.Remove('directory')
    $state | ConvertTo-Json -Depth 5 | Set-Content (Join-Path $workspace "reports\beta-installer-result$suffix.json") -Encoding utf8
    $state | ConvertTo-Json -Depth 5
    if ($remove.ExitCode -ne 0 -or -not $state.profile_unchanged -or -not $state.program_removed -or -not $state.shortcuts_removed -or -not $state.registration_removed) {exit 1}
}
