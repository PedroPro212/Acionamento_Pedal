# FS-01 Disparador da Câmera

Aplicativo para Windows desenvolvido para integrar o **pedal USB FS-01 /
LinTx** a aplicações de câmera. O software monitora diretamente o
dispositivo HID e, ao detectar o acionamento do pedal, envia a tecla
**Espaço** ao Windows, permitindo realizar o disparo sem utilizar o
mouse.

Desenvolvido pela **Programação Diária** e **Flash Informática**.

## Funcionalidades

-   Detecção automática do pedal FS-01 via USB/HID
-   Comunicação direta com o dispositivo, sem depender do ElfKey
-   Acionamento da tecla `Espaço` ao pressionar o pedal
-   Reconexão automática caso o pedal seja desconectado
-   Interface gráfica para acompanhamento do dispositivo
-   Exibição de produto e número de série
-   Contador de acionamentos e registro de atividades
-   Inicialização automática com o Windows
-   Suporte à execução em segundo plano/bandeja do sistema
-   Executável independente com PyInstaller
-   Instalador para Windows com Inno Setup

## Hardware identificado

  Propriedade             Valor
  ----------------------- -----------------------------------
  Fabricante              LinTx
  Produto                 LinTx HID Device / LinTx Keyboard
  VID                     `8088`
  PID                     `0015`
  Interface utilizada     HID proprietária
  Usage Page              `0xFF00`
  Pacote de acionamento   `66 CC 03 00 01`

O dispositivo também apresenta interfaces HID de teclado. Este projeto
utiliza diretamente a interface proprietária para detectar o
acionamento.

## Como funciona

O software procura um dispositivo com:

``` text
VID: 8088
PID: 0015
Usage Page: 0xFF00
```

Quando o pedal é pressionado, é recebido um relatório HID de 64 bytes
cujo início é:

``` text
66 CC 03 00 01
```

Ao reconhecer esse pacote, o programa utiliza a API do Windows para
simular a tecla `Espaço`.

``` text
FS-01
  ↓
USB / HID
  ↓
FS01_Camera
  ↓
Detecção do pacote
  ↓
Tecla Espaço
  ↓
Aplicativo de câmera
  ↓
Disparo
```

## Requisitos para desenvolvimento

-   Windows 10 ou Windows 11
-   Python 3
-   Pedal USB compatível
-   `hidapi`
-   `Pillow`
-   `pystray`
-   `PyInstaller`

Instale as dependências:

``` powershell
pip install hidapi Pillow pystray pyinstaller
```

> O usuário final não precisa instalar Python nem essas bibliotecas
> quando utiliza a versão compilada.

## Executando pelo código-fonte

``` powershell
python index.py
```

Com o pedal conectado, o software deverá localizar automaticamente o
dispositivo compatível.

## Gerando o executável

O projeto utiliza PyInstaller para criar um executável independente.

``` bat
python -m PyInstaller ^
 --noconfirm ^
 --clean ^
 --onefile ^
 --windowed ^
 --name FS01_Camera ^
 --icon "..\logoSistema.ico" ^
 --add-data "..\logoFlash.png;." ^
 --add-data "..\logoProgramacaoDiaria.png;." ^
 "..\index.py"
```

Após a compilação:

``` text
dist\FS01_Camera.exe
```

## Instalador

O instalador é criado com **Inno Setup** e pode instalar o programa em
`Program Files`, criar atalhos, adicionar o aplicativo ao Menu Iniciar,
configurar a inicialização automática e fornecer um desinstalador.

O usuário final precisa apenas executar:

``` text
Instalador_FS01_Camera.exe
```

## Inicialização automática

A instalação pode registrar o aplicativo em:

``` text
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
```

Assim, após o login no Windows, o FS-01 Camera é iniciado
automaticamente e começa a monitorar o pedal.

## Execução em segundo plano

O aplicativo pode permanecer na bandeja do sistema:

``` text
Windows inicia
      ↓
Usuário faz login
      ↓
FS01_Camera inicia
      ↓
Monitoramento HID é iniciado
      ↓
Aplicativo permanece na bandeja
      ↓
Pedal pronto para uso
```

O painel pode ser aberto pelo ícone da bandeja quando necessário.

## Observação sobre o disparo

Atualmente o aplicativo simula a tecla `Espaço` utilizando a API do
Windows. Portanto, a aplicação que deve receber o comando precisa estar
preparada para responder a essa tecla.

## Reconexão automática

Se o FS-01 for removido da porta USB durante a execução, o software
encerra a conexão HID atual e continua procurando pelo dispositivo.
Quando o pedal é conectado novamente, o monitoramento é retomado
automaticamente.

## Estrutura sugerida

``` text
Acionamento_Pedal/
│
├── index.py
├── logoFlash.png
├── logoProgramacaoDiaria.png
├── logoSistema.ico
├── README.md
│
└── Documentação/
    ├── gerar_exe_interface.bat
    ├── FS01_Camera.iss
    ├── dist/
    │   └── FS01_Camera.exe
    └── Instalador/
        └── Instalador_FS01_Camera.exe
```

## Compatibilidade

O software foi desenvolvido a partir do protocolo observado no hardware
FS-01/LinTx testado. Outras revisões podem utilizar VID, PID, Usage Page
ou pacotes HID diferentes e exigir adaptações.

## Tecnologias

Python · Tkinter · hidapi · Pillow · pystray · Windows API · PyInstaller
· Inno Setup

## Segurança

O aplicativo não necessita de acesso à internet para monitorar o pedal.
A comunicação é realizada localmente através da interface USB/HID do
Windows.

Executáveis distribuídos sem certificado de assinatura de código podem
gerar um aviso do Microsoft Defender SmartScreen indicando fornecedor
desconhecido.

## Autor

**Flash Informática**

Projeto desenvolvido para integração do pedal USB FS-01 com aplicações
de câmera no Windows.

## Licença

Defina a licença do projeto antes de distribuí-lo publicamente. Caso o
código seja proprietário, substitua esta seção pelos termos de uso
apropriados.
