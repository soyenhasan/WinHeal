[Setup]
AppName=WinHeal
AppVersion=0.6.0
DefaultDirName={pf}\WinHeal
DefaultGroupName=WinHeal
OutputDir=.
OutputBaseFilename=WinHeal-Setup-v0.6.0
SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\WinHeal-v0.6.0-PRO-ULTRA.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\WinHeal"; Filename: "{app}\WinHeal-v0.6.0-PRO-ULTRA.exe"
Name: "{commondesktop}\WinHeal"; Filename: "{app}\WinHeal-v0.6.0-PRO-ULTRA.exe"
Name: "{group}\Uninstall WinHeal"; Filename: "{uninstallexe}"