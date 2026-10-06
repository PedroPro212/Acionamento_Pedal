# FS-01 Disparador da Câmera --- Comandos do Projeto

Guia rápido dos principais comandos usados para desenvolver, testar,
compilar e instalar o **FS-01 Disparador da Câmera**.

## 1. Acessar o projeto

``` powershell
cd C:\Codigos\Acionamento_Pedal
```

## 2. Verificar Python e pip

``` powershell
python --version
python -m pip --version
```

## 3. Instalar dependências

`requirements.txt`:

``` txt
hidapi>=0.14.0
Pillow>=10.0.0
pyinstaller>=6.0
pystray
```

Instalação:

``` powershell
python -m pip install -r requirements.txt
```

Ou:

``` powershell
python -m pip install hidapi Pillow pyinstaller pystray
```

## 4. Atualizar dependências

``` powershell
python -m pip install --upgrade hidapi Pillow pyinstaller pystray
```

## 5. Validar a sintaxe do código

``` powershell
python -m py_compile index.py
```

Se não aparecer nenhuma mensagem, a sintaxe está correta.

## 6. Executar pelo Python

``` powershell
python index.py
```

Na versão com bandeja, o programa pode iniciar escondido. Verifique a
seta `^` próxima ao relógio do Windows.

## 7. Gerar o executável

Considerando `index.py` e as duas logos na raiz e `logoSistema.ico`
dentro de `Documentação`, entre na pasta:

``` powershell
cd C:\Codigos\Acionamento_Pedal\Documentação
```

Depois:

``` powershell
python -m PyInstaller --noconfirm --clean --onefile --windowed --name FS01_Camera --icon "logoSistema.ico" --add-data "logoSistema.ico;." --add-data "..\logoFlash.png;." --add-data "..\logoProgramacaoDiaria.png;." "..\index.py"
```

O executável será criado em:

``` text
Documentação\dist\FS01_Camera.exe
```

> Se `logoSistema.ico` estiver na raiz do projeto, troque
> `logoSistema.ico` por `..\logoSistema.ico` nos parâmetros
> correspondentes.

### Principais opções do PyInstaller

-   `--noconfirm`: sobrescreve o build anterior sem confirmação.
-   `--clean`: limpa o cache de compilação.
-   `--onefile`: cria um único executável.
-   `--windowed`: não exibe console junto com a interface.
-   `--name`: nome do executável.
-   `--icon`: ícone do executável.
-   `--add-data`: adiciona imagens e outros arquivos ao pacote.

## 8. Gerar pelo BAT

``` powershell
cd C:\Codigos\Acionamento_Pedal\Documentação
.\gerar_exe_interface.bat
```

Exemplo do BAT:

``` bat
@echo off
title Gerando FS-01 Camera

python -m PyInstaller ^
 --noconfirm ^
 --clean ^
 --onefile ^
 --windowed ^
 --name FS01_Camera ^
 --icon "logoSistema.ico" ^
 --add-data "logoSistema.ico;." ^
 --add-data "..\logoFlash.png;." ^
 --add-data "..\logoProgramacaoDiaria.png;." ^
 "..\index.py"

pause
```

## 9. Limpar builds antigos

PowerShell:

``` powershell
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
Remove-Item FS01_Camera.spec -Force -ErrorAction SilentlyContinue
```

Prompt de Comando:

``` cmd
rmdir /s /q build
rmdir /s /q dist
del FS01_Camera.spec
```

## 10. Testar o executável

Dentro de `Documentação`:

``` powershell
.\dist\FS01_Camera.exe
```

Comportamento esperado: iniciar na bandeja, monitorar o FS-01
automaticamente, enviar Espaço quando o pedal for acionado, abrir o
painel pelo ícone da bandeja e encerrar pela opção **Sair**.

## 11. Gerar instalador no Inno Setup

Depois de gerar `dist\FS01_Camera.exe`, abra o arquivo `.iss` no Inno
Setup Compiler e use:

``` text
Build → Compile
```

Atalho:

``` text
Ctrl + F9
```

Se o `.iss` estiver configurado com `OutputDir=Instalador`, o resultado
ficará, por exemplo, em:

``` text
Instalador\Instalador_FS01_Camera.exe
```

## 12. Inicialização automática com o Windows

Entrada usada no Inno Setup:

``` ini
[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "FS01Camera"; ValueData: """{app}\{#MyAppExeName}"""; Flags: uninsdeletevalue
```

Para conferir os aplicativos de inicialização:

``` text
Ctrl + Shift + Esc
```

Depois abra **Aplicativos de Inicialização**.

## 13. Diagnóstico das bibliotecas

HID:

``` powershell
python -c "import hid; print('hidapi OK')"
```

Pillow:

``` powershell
python -c "from PIL import Image; print('Pillow OK')"
```

pystray:

``` powershell
python -c "import pystray; print('pystray OK')"
```

Tudo de uma vez:

``` powershell
python -c "import hid, pystray; from PIL import Image, ImageTk; print('Dependencias OK')"
```

## 14. Fluxo recomendado depois de alterar o código

``` powershell
cd C:\Codigos\Acionamento_Pedal

python -m py_compile index.py
python index.py

cd .\Documentação
.\gerar_exe_interface.bat
.\dist\FS01_Camera.exe
```

Depois que o executável estiver validado, compile novamente o instalador
no Inno Setup.

## Resumo rápido

``` powershell
# Instalar dependências
python -m pip install -r requirements.txt

# Validar
python -m py_compile index.py

# Executar
python index.py

# Compilar
cd .\Documentação
.\gerar_exe_interface.bat

# Testar executável
.\dist\FS01_Camera.exe
```

------------------------------------------------------------------------

**Projeto:** FS-01 Disparador da Câmera\
**Desenvolvimento:** Flash Informática
