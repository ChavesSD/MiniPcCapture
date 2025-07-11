@echo off
echo   COMPILADOR - Screnoid
echo ================================================

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [31mERRO: Python nao encontrado![0m
    echo Instale Python 3.8 ou superior
    pause
    exit /b 1
)

REM Verificar pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [31mERRO: pip nao encontrado![0m
    echo Reinstale o Python com a opcao "Add pip to PATH" marcada
    pause
    exit /b 1
)

REM Criar ambiente virtual
echo.
echo Criando ambiente virtual...
python -m venv venv
if %errorlevel% neq 0 (
    echo [31mERRO ao criar ambiente virtual![0m
    pause
    exit /b 1
)

REM Ativar ambiente
call venv\Scripts\activate

REM Instalar dependências
echo.
echo Instalando dependencias...
pip install -r requirements.txt
pip install auto-py-to-exe

REM Criar arquivo de configuração
echo.
echo Criando configuracao...
echo { > auto-py-to-exe-config.json
echo   "version": "auto-py-to-exe-configuration_v1", >> auto-py-to-exe-config.json
echo   "pyinstallerOptions": [ >> auto-py-to-exe-config.json
echo     { >> auto-py-to-exe-config.json
echo       "optionDest": "noconfirm", >> auto-py-to-exe-config.json
echo       "value": true >> auto-py-to-exe-config.json
echo     }, >> auto-py-to-exe-config.json
echo     { >> auto-py-to-exe-config.json
echo       "optionDest": "filenames", >> auto-py-to-exe-config.json
echo       "value": "main.py" >> auto-py-to-exe-config.json
echo     }, >> auto-py-to-exe-config.json
echo     { >> auto-py-to-exe-config.json
echo       "optionDest": "onefile", >> auto-py-to-exe-config.json
echo       "value": false >> auto-py-to-exe-config.json
echo     }, >> auto-py-to-exe-config.json
echo     { >> auto-py-to-exe-config.json
echo       "optionDest": "console", >> auto-py-to-exe-config.json
echo       "value": false >> auto-py-to-exe-config.json
echo     }, >> auto-py-to-exe-config.json
echo     { >> auto-py-to-exe-config.json
echo       "optionDest": "name", >> auto-py-to-exe-config.json
echo       "value": "Screnoid">> auto-py-to-exe-config.json
echo     }, >> auto-py-to-exe-config.json
echo     { >> auto-py-to-exe-config.json
echo       "optionDest": "ascii", >> auto-py-to-exe-config.json
echo       "value": false >> auto-py-to-exe-config.json
echo     }, >> auto-py-to-exe-config.json
echo     { >> auto-py-to-exe-config.json
echo       "optionDest": "clean_build", >> auto-py-to-exe-config.json
echo       "value": false >> auto-py-to-exe-config.json
echo     }, >> auto-py-to-exe-config.json
echo     { >> auto-py-to-exe-config.json
echo       "optionDest": "strip", >> auto-py-to-exe-config.json
echo       "value": false >> auto-py-to-exe-config.json
echo     }, >> auto-py-to-exe-config.json
echo     { >> auto-py-to-exe-config.json
echo       "optionDest": "noupx", >> auto-py-to-exe-config.json
echo       "value": false >> auto-py-to-exe-config.json
echo     }, >> auto-py-to-exe-config.json
echo     { >> auto-py-to-exe-config.json
echo       "optionDest": "disable_windowed_traceback", >> auto-py-to-exe-config.json
echo       "value": false >> auto-py-to-exe-config.json
echo     }, >> auto-py-to-exe-config.json
echo     { >> auto-py-to-exe-config.json
echo       "optionDest": "embed_manifest", >> auto-py-to-exe-config.json
echo       "value": true >> auto-py-to-exe-config.json
echo     }, >> auto-py-to-exe-config.json
echo     { >> auto-py-to-exe-config.json
echo       "optionDest": "uac_admin", >> auto-py-to-exe-config.json
echo       "value": false >> auto-py-to-exe-config.json
echo     }, >> auto-py-to-exe-config.json
echo     { >> auto-py-to-exe-config.json
echo       "optionDest": "uac_uiaccess", >> auto-py-to-exe-config.json
echo       "value": false >> auto-py-to-exe-config.json
echo     }, >> auto-py-to-exe-config.json
echo     { >> auto-py-to-exe-config.json
echo       "optionDest": "win_private_assemblies", >> auto-py-to-exe-config.json
echo       "value": false >> auto-py-to-exe-config.json
echo     }, >> auto-py-to-exe-config.json
echo     { >> auto-py-to-exe-config.json
echo       "optionDest": "win_no_prefer_redirects", >> auto-py-to-exe-config.json
echo       "value": false >> auto-py-to-exe-config.json
echo     }, >> auto-py-to-exe-config.json
echo     { >> auto-py-to-exe-config.json
echo       "optionDest": "bootloader_ignore_signals", >> auto-py-to-exe-config.json
echo       "value": false >> auto-py-to-exe-config.json
echo     } >> auto-py-to-exe-config.json
echo   ], >> auto-py-to-exe-config.json
echo   "nonPyinstallerOptions": { >> auto-py-to-exe-config.json
echo     "increaseRecursionLimit": true, >> auto-py-to-exe-config.json
echo     "manualArguments": "" >> auto-py-to-exe-config.json
echo   } >> auto-py-to-exe-config.json
echo } >> auto-py-to-exe-config.json

REM Compilar
echo.
echo Compilando...
python build_config.py

REM Verificar resultado
if exist "dist\Screnoid\Screnoid.exe" (
    echo.
    echo [32mCompilacao concluida com sucesso![0m
    echo.
    echo Arquivos gerados:
    echo dist\Screnoid\Screnoid.exe
    echo.
    echo Para distribuir:
    echo 1. Copie toda a pasta 'dist\Screnoid'
    echo 2. Execute o Screnoid.exe na pasta copiada
    echo.
) else (
    echo [31mERRO: Falha na compilacao![0m
    echo Verifique os erros acima
)

REM Limpar
call venv\Scripts\deactivate
rmdir /s /q venv

pause 