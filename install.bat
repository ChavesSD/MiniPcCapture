@echo off
echo ========================================
echo  Instalador - Gravador de Tela Android
echo ========================================
echo.

:: Verificar se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python não está instalado!
    echo.
    echo Por favor, instale Python 3.7+ em:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo ✓ Python encontrado
echo.

:: Verificar se ADB local existe
if exist "platform-tools\adb.exe" (
    echo ✓ ADB local encontrado em platform-tools\
    echo.
) else (
    echo AVISO: ADB local não encontrado!
    echo.
    echo Verificando ADB do sistema...
    adb version >nul 2>&1
    if %errorlevel% neq 0 (
        echo.
        echo ERRO: Nem ADB local nem ADB do sistema foram encontrados!
        echo.
        echo OPÇÕES:
        echo 1. Baixe Platform Tools e extraia na pasta 'platform-tools'
        echo    Link: https://developer.android.com/studio/releases/platform-tools
        echo.
        echo 2. Ou instale ADB no sistema e adicione ao PATH
        echo.
        echo Deseja baixar Platform Tools automaticamente? (s/n)
        set /p download_adb=
        if /i "%download_adb%"=="s" (
            echo.
            echo Baixando Platform Tools...
            powershell -Command "try { Invoke-WebRequest -Uri 'https://dl.google.com/android/repository/platform-tools-latest-windows.zip' -OutFile 'platform-tools.zip' -UseBasicParsing } catch { Write-Host 'Erro ao baixar. Verifique sua conexão.' -ForegroundColor Red; exit 1 }"
            
            if exist "platform-tools.zip" (
                echo Extraindo...
                powershell -Command "try { Expand-Archive -Path 'platform-tools.zip' -DestinationPath '.' -Force } catch { Write-Host 'Erro ao extrair.' -ForegroundColor Red; exit 1 }"
                del platform-tools.zip >nul 2>&1
                
                if exist "platform-tools\adb.exe" (
                    echo ✓ Platform Tools instalado com sucesso!
                ) else (
                    echo ERRO: Falha na instalação do Platform Tools
                    pause
                    exit /b 1
                )
            ) else (
                echo ERRO: Falha no download
                pause
                exit /b 1
            )
        ) else (
            echo.
            echo Por favor, instale o ADB manualmente e execute novamente.
            pause
            exit /b 1
        )
    ) else (
        echo ✓ ADB do sistema encontrado
    )
)

echo.

:: Instalar dependências
echo Instalando dependências opcionais...
pip install -r requirements.txt

:: Verificar instalação
echo.
echo Verificando instalação...

:: Testar ADB
if exist "platform-tools\adb.exe" (
    "platform-tools\adb.exe" version >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✓ ADB local funcionando
    ) else (
        echo ⚠ ADB local com problemas
    )
) else (
    adb version >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✓ ADB sistema funcionando
    ) else (
        echo ⚠ ADB com problemas
    )
)

:: Testar Python
python -c "import tkinter" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Interface gráfica (tkinter) disponível
) else (
    echo ⚠ Problema com interface gráfica
)

echo.
echo ========================================
echo  Instalação Concluída!
echo ========================================
echo.
echo Para executar o software:
echo   executar.bat
echo   ou
echo   python main.py
echo.
echo IMPORTANTE:
echo - Ative "Depuração USB" no Android
echo - Autorize o computador quando conectar
echo - Para mini PCs: conecte via USB ou configure Wi-Fi
echo.

:: Perguntar se quer executar agora
set /p run_now=Deseja executar o software agora? (s/n): 
if /i "%run_now%"=="s" (
    echo.
    echo Iniciando Gravador de Tela Android...
    python main.py
)

pause 