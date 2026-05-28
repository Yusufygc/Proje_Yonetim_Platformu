#define MyAppName "Proje Takip Platformu"
#define MyAppVersion "0.1.0"
#define MyAppExeName "ProjeTakipPlatformu.exe"

[Setup]
AppId={{99B49D61-13F5-4CE1-8D86-9E569F516358}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\ProjeTakipPlatformu
DefaultGroupName={#MyAppName}
OutputDir=..\dist\installer
OutputBaseFilename=ProjeTakipPlatformuSetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "..\dist\ProjeTakipPlatformu\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Masaustu kisayolu olustur"; GroupDescription: "Ek kisayollar:"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{#MyAppName} uygulamasini baslat"; Flags: nowait postinstall skipifsilent
