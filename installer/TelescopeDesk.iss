; Per-user install; no auth files/configuration, no automatic application launch.
#ifndef AppVersion
  #error AppVersion must be supplied by build-installer.ps1 from project metadata
#endif
#ifndef SourceRoot
  #define SourceRoot "..\dist\" + AppVersion + "\TelescopeDesk"
#endif

[Setup]
AppId={{BF344EF3-C3B3-4514-8B99-57CA7F157280}
AppName=Telescope Desk
AppVersion={#AppVersion}
AppPublisher=Telescope Desk
DefaultDirName={localappdata}\Programs\TelescopeDesk
DefaultGroupName=Telescope Desk
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
DisableProgramGroupPage=yes
UsePreviousAppDir=yes
WizardStyle=modern dynamic
LicenseFile=..\LICENSE
InfoBeforeFile=INSTALLER-NOTES.txt
UninstallDisplayIcon={app}\TelescopeDesk.exe
SetupIconFile=..\telescope_desk\assets\TelescopeDesk.ico
OutputDir=..\release
OutputBaseFilename=TelescopeDesk-{#AppVersion}-setup-win64
Compression=lzma2
SolidCompression=yes
AppMutex=Local\SeestarStudio.Main
CloseApplications=no
RestartApplications=no
SetupLogging=no

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:DesktopShortcut}"; GroupDescription: "{cm:AdditionalShortcuts}"; Flags: unchecked

[CustomMessages]
german.DesktopShortcut=Desktopverknüpfung erstellen
german.AdditionalShortcuts=Zusätzliche Verknüpfungen:
english.DesktopShortcut=Create a desktop shortcut
english.AdditionalShortcuts=Additional shortcuts:

[Files]
Source: "{#SourceRoot}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Telescope Desk"; Filename: "{app}\TelescopeDesk.exe"; WorkingDir: "{app}"; IconFilename: "{app}\TelescopeDesk.exe"; AppUserModelID: "TelescopeDesk.Desktop"
Name: "{autodesktop}\Telescope Desk"; Filename: "{app}\TelescopeDesk.exe"; WorkingDir: "{app}"; IconFilename: "{app}\TelescopeDesk.exe"; AppUserModelID: "TelescopeDesk.Desktop"; Tasks: desktopicon

; No [Run], [InstallDelete] or [UninstallDelete]: never start hardware access
; automatically or delete user-profile settings, authentication or history.
