@echo off
echo Iniciando Gravador de Tela Android...
echo.

:: Verificar se main.py existe
if not exist "main.py" (
    echo ERRO: Arquivo main.py não encontrado!
    echo Certifique-se de estar na pasta correta do projeto.
    pause
    exit /b 1
)

:: Executar o programa
python main.py

:: Pausa se houver erro
if %errorlevel% neq 0 (
    echo.
    echo ERRO: O programa terminou inesperadamente!
    echo Verifique se Python e ADB estão instalados corretamente.
    pause
) 