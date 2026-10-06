#define MyAppName "FS-01 Disparador da Câmera"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Flash Informática"
#define MyAppExeName "FS01_Camera.exe"
#define MyAppIcon "logoSistema.ico"

[Setup]
AppId={{7A53B1C2-DF24-4D47-9A30-FS0100012026}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

DefaultDirName={autopf}\Flash Informática\FS-01 Camera
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; ============================================================
; SAÍDA
; ============================================================

OutputDir=Instalador
OutputBaseFilename=Instalador_FS01_Camera

Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin

; ============================================================
; ÍCONE DO INSTALADOR
; ============================================================

SetupIconFile={#MyAppIcon}

; ============================================================
; DESINSTALADOR
; ============================================================

UninstallDisplayName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppIcon}

; ============================================================
; ARQUITETURA
; ============================================================

ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible


[Files]

; Programa principal
Source: "dist\FS01_Camera.exe"; \
DestDir: "{app}"; \
Flags: ignoreversion

; Ícone
Source: "{#MyAppIcon}"; \
DestDir: "{app}"; \
Flags: ignoreversion


[Tasks]

; Atalho opcional na Área de Trabalho
Name: "desktopicon"; \
Description: "Criar atalho na Área de Trabalho"; \
GroupDescription: "Atalhos:"; \
Flags: unchecked


[Icons]

; Menu Iniciar
Name: "{group}\{#MyAppName}"; \
Filename: "{app}\{#MyAppExeName}"; \
IconFilename: "{app}\{#MyAppIcon}"

; Área de Trabalho
Name: "{autodesktop}\{#MyAppName}"; \
Filename: "{app}\{#MyAppExeName}"; \
IconFilename: "{app}\{#MyAppIcon}"; \
Tasks: desktopicon


[Registry]

; Iniciar automaticamente com o Windows
Root: HKCU; \
Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; \
ValueType: string; \
ValueName: "FS01Camera"; \
ValueData: """{app}\{#MyAppExeName}"""; \
Flags: uninsdeletevalue


[Run]

; Abrir após instalação
Filename: "{app}\{#MyAppExeName}"; \
Description: "Abrir {#MyAppName}"; \
Flags: nowait postinstall skipifsilent