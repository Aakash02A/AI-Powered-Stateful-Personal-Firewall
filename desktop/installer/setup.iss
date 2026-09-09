[Setup]
AppName=AI-Powered Personal Firewall
AppVersion=1.1.0
AppPublisher=Antigravity
DefaultDirName={pf}\AIFirewall
DefaultGroupName=AI Firewall
OutputDir=..\release
OutputBaseFilename=AIFirewall_Setup_v1.1.0
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin

[Files]
Source: "..\dist\AIFirewall\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Note: Inno Setup would extract pydivert/WinDivert drivers here if specifically handling driver install.
; Pydivert PyInstaller hooks normally bundle the driver .sys and .dll files.

[Icons]
Name: "{group}\AI Firewall Dashboard"; Filename: "{app}\ai_firewall_dashboard.exe"
Name: "{group}\AI Firewall Tray"; Filename: "{app}\ai_firewall_tray.exe"
Name: "{commondesktop}\AI Firewall"; Filename: "{app}\ai_firewall_tray.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"

[Run]
; Register and Start the service
Filename: "{app}\firewall_service.exe"; Parameters: "--startup auto install"; Flags: runhidden
Filename: "{app}\firewall_service.exe"; Parameters: "start"; Flags: runhidden
; Start the tray app for the current user
Filename: "{app}\ai_firewall_tray.exe"; Flags: nowait postinstall; Description: "Launch AI Firewall Tray"

[Registry]
; Auto-start tray app on login
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "AIFirewallTray"; ValueData: """{app}\ai_firewall_tray.exe"""; Flags: uninsdeletevalue

[UninstallRun]
; Stop and remove the service
Filename: "{app}\firewall_service.exe"; Parameters: "stop"; Flags: runhidden
Filename: "{app}\firewall_service.exe"; Parameters: "remove"; Flags: runhidden
