#define MyAppVersion "0.7.0"
#define MyAppExeName "WinHeal.exe"

[Setup]
AppId={{8A5F7E2C-9B3D-4A1E-B2C8-D9F0E1A2B3C4}
AppName=WinHeal
AppVersion={#MyAppVersion}
AppPublisher=Soyen Hasan - Made in Bangladesh
AppPublisherURL=https://github.com/soyenhasan/WinHeal-AI
DefaultDirName={pf}\WinHeal
DefaultGroupName=WinHeal
OutputBaseFilename=WinHeal-Setup-v0.7.0-LEGEND
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesInstallIn64BitMode=x64

[Files]
Source: "dist\WinHeal.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\WinHeal"; Filename: "{app}\WinHeal.exe"; IconFilename: "{app}\icon.ico"
Name: "{autodesktop}\WinHeal"; Filename: "{app}\WinHeal.exe"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon
[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; Flags: unchecked
[Run]
Filename: "{app}\WinHeal.exe"; Flags: nowait postinstall skipifsilent