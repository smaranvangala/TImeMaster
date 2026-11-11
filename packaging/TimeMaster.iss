; Per-user install; uninstall never removes the user's saved database.
#define MyAppVersion "0.1.0"
[Setup]
AppId={{D9A7A44F-08CF-4B4A-BFF2-6B720D26E0B7}
AppName=TimeMaster
AppVersion={#MyAppVersion}
DefaultDirName={localappdata}\Programs\TimeMaster
DefaultGroupName=TimeMaster
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=..\dist
OutputBaseFilename=TimeMaster-{#MyAppVersion}-setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\TimeMaster.exe
[Files]
Source: "..\dist\TimeMaster\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Tasks]
Name: desktopicon; Description: "Create a desktop shortcut"; Flags: unchecked
[Icons]
Name: "{group}\TimeMaster"; Filename: "{app}\TimeMaster.exe"
Name: "{autodesktop}\TimeMaster"; Filename: "{app}\TimeMaster.exe"; Tasks: desktopicon
[Run]
Filename: "{app}\TimeMaster.exe"; Description: "Launch TimeMaster"; Flags: nowait postinstall skipifsilent
