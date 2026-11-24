; Proje Takip Platformu kurulum sihirbazi (Inno Setup 6). Derleme: python build_installer.py (surum /DAppVersion ile gelir)
#ifndef AppVersion
  #error AppVersion tanimli degil: python build_installer.py ile derle
#endif

[Setup]
; AppId SABIT: degisirse sonraki surum ustune yazmaz, ikinci kurulum olur (eski kurulumlarla da ayni)
AppId={{99B49D61-13F5-4CE1-8D86-9E569F516358}
AppName=Proje Takip Platformu
AppVersion={#AppVersion}
AppVerName=Proje Takip Platformu {#AppVersion}
AppPublisher=ProjeTakip
AppPublisherURL=https://github.com/Yusufygc/Proje_Yonetim_Platformu
AppSupportURL=https://github.com/Yusufygc/Proje_Yonetim_Platformu
; PrivilegesRequired=lowest iken {autopf} = %LOCALAPPDATA%\Programs
DefaultDirName={autopf}\ProjeTakipPlatformu
DefaultGroupName=Proje Takip Platformu
; UAC sormaz: guncelleme sessiz calisir, derleme sonrasi deneme mumkun olur
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
; Guncellemede calisan uygulama kapatilir (dosya kilidi olmasin); yeniden acmayi [Run] yapar
CloseApplications=yes
RestartApplications=no
SetupIconFile=..\icons\app_icon.ico
UninstallDisplayIcon={app}\ProjeTakipPlatformu.exe
OutputDir=..\dist\installer
; Surumlu ad: guncelleyici bu desene bakar (ProjeTakipPlatformu-Setup-X.Y.Z.exe)
OutputBaseFilename=ProjeTakipPlatformu-Setup-{#AppVersion}
Compression=lzma2/max
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern
DisableProgramGroupPage=yes

[Languages]
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\ProjeTakipPlatformu\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Proje Takip Platformu"; Filename: "{app}\ProjeTakipPlatformu.exe"; IconFilename: "{app}\_internal\icons\app_icon.ico"
Name: "{autodesktop}\Proje Takip Platformu"; Filename: "{app}\ProjeTakipPlatformu.exe"; IconFilename: "{app}\_internal\icons\app_icon.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\ProjeTakipPlatformu.exe"; Description: "{cm:LaunchProgram,Proje Takip Platformu}"; Flags: nowait postinstall skipifsilent
; Uygulama ici guncelleme (/SILENT): kurulumdan sonra uygulama kendiliginden yeniden acilir
Filename: "{app}\ProjeTakipPlatformu.exe"; Flags: nowait; Check: RelaunchAfterUpdate

; Kullanici verisi (%LOCALAPPDATA%\ProjeTakip: veritabani, gunluk) kaldirici tarafindan SILINMEZ.

[Code]
function HasParam(const Name: String): Boolean;
var
  I: Integer;
begin
  Result := False;
  for I := 1 to ParamCount do
    if CompareText(ParamStr(I), Name) = 0 then
    begin
      Result := True;
      Exit;
    end;
end;

{ /SILENT (guncelleme) yeniden acar; /VERYSILENT (derleme sonrasi deneme) acmaz. WizardVerySilent diye bir islev yoktur. }
function RelaunchAfterUpdate: Boolean;
begin
  Result := WizardSilent and not HasParam('/VERYSILENT');
end;
