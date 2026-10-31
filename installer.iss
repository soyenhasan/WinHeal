[Setup]
AppName=WinHeal
AppVersion=0.6.1
DefaultDirName={pf}\WinHeal
DefaultGroupName=WinHeal
OutputDir=.
OutputBaseFilename=WinHeal-Setup-v0.6.1
SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\WinHeal.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\WinHeal"; Filename: "{app}\WinHeal.exe"
Name: "{commondesktop}\WinHeal"; Filename: "{app}\WinHeal.exe"
Name: "{group}\Uninstall WinHeal"; Filename: "{uninstallexe}"