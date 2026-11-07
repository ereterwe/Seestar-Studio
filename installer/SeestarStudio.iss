; Per-user install; no auth files/configuration, no automatic application launch.
#ifndef AppVersion
  #error AppVersion must be supplied by build-installer.ps1 from project metadata
#endif
#ifndef SourceRoot
  #define SourceRoot "..\dist\" + AppVersion + "\SeestarStudio"
#endif

[Setup]
AppId={{A8B6B872-6710-44A3-94A6-1C953E3B8D87}
AppName=Seestar Studio
AppVersion={#AppVersion}
AppPublisher=Seestar Studio
DefaultDirName={localappdata}\Programs\SeestarStudio
DefaultGroupName=Seestar Studio
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
DisableProgramGroupPage=yes
UsePreviousAppDir=yes
WizardStyle=modern dynamic
LicenseFile=..\LICENSE
InfoBeforeFile=INSTALLER-NOTES.txt
UninstallDisplayIcon={app}\SeestarStudio.exe
SetupIconFile=..\seestar_studio\assets\SeestarStudio.ico
OutputDir=..\release
OutputBaseFilename=SeestarStudio-{#AppVersion}-setup-win64
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
Name: "{autoprograms}\Seestar Studio"; Filename: "{app}\SeestarStudio.exe"; WorkingDir: "{app}"; IconFilename: "{app}\SeestarStudio.exe"; AppUserModelID: "SeestarStudio.Desktop"
Name: "{autodesktop}\Seestar Studio"; Filename: "{app}\SeestarStudio.exe"; WorkingDir: "{app}"; IconFilename: "{app}\SeestarStudio.exe"; AppUserModelID: "SeestarStudio.Desktop"; Tasks: desktopicon

; No [Run], [InstallDelete] or [UninstallDelete]: never start hardware access
; automatically or delete user-profile settings, authentication or history.
