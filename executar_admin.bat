@echo off
:: Verifica se está rodando como administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Solicitando privilégios de administrador...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo ========================================
echo  Gravador de Tela Android (Admin Mode)
echo ========================================
echo.

:: Obtém o diretório do script
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: Verificar se main.py existe
if not exist "%SCRIPT_DIR%main.py" (
    echo ERRO: Arquivo main.py não encontrado!
    echo Certifique-se de estar na pasta correta do projeto.
    echo Diretório atual: %SCRIPT_DIR%
    pause
    exit /b 1
)

:: Executar o programa
python "%SCRIPT_DIR%main.py"

:: Pausa se houver erro
if %errorlevel% neq 0 (
    echo.
    echo ERRO: O programa terminou inesperadamente!
    echo Verifique se Python e ADB estão instalados corretamente.
    pause
) 