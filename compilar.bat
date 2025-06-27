@echo off
echo ===============================================
echo   COMPILADOR - MiniPc Capture
echo ===============================================
echo.

:: Verificar se Python está disponível
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python não encontrado!
    echo Instale Python primeiro: https://python.org
    pause
    exit /b 1
)

echo ✓ Python encontrado
echo.

:: Verificar arquivos necessários
if not exist "main.py" (
    echo ERRO: main.py não encontrado!
    pause
    exit /b 1
)

if not exist "platform-tools" (
    echo ERRO: Pasta platform-tools não encontrada!
    echo Certifique-se de que está na pasta correta do projeto.
    pause
    exit /b 1
)

echo ✓ Arquivos verificados
echo.

:: Instalar PyInstaller se necessário
echo Verificando PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando PyInstaller...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo ERRO: Falha ao instalar PyInstaller
        pause
        exit /b 1
    )
)

echo ✓ PyInstaller pronto
echo.

:: Limpar compilações anteriores
if exist "dist" (
    echo Limpando compilação anterior...
    rmdir /s /q dist 2>nul
)

if exist "build" (
    rmdir /s /q build 2>nul
)

:: Compilar
echo ==========================================
echo   COMPILANDO EXECUTÁVEL...
echo ==========================================
echo.

pyinstaller --onedir --windowed --name "MiniPcCapture" --add-data "platform-tools;platform-tools" --distpath "dist" --workpath "build" main.py

:: Verificar resultado
if %errorlevel% equ 0 (
    echo.
    echo ==========================================
    echo   ✅ COMPILAÇÃO CONCLUÍDA COM SUCESSO!
    echo ==========================================
    echo.
    echo 📁 Pasta do executável: dist\MiniPcCapture\
    echo 📋 Arquivo principal: MiniPcCapture.exe
    echo.
    
    :: Verificar se executável existe
    if exist "dist\MiniPcCapture\MiniPcCapture.exe" (
        echo ✓ Executável criado com sucesso
        
        :: Verificar platform-tools
        if exist "dist\MiniPcCapture\platform-tools\adb.exe" (
            echo ✓ ADB incluído corretamente
        ) else (
            echo ⚠ AVISO: ADB pode não ter sido incluído
        )
        
        echo.
        echo PRÓXIMOS PASSOS:
        echo 1. Teste o executável executando dist\MiniPcCapture\MiniPcCapture.exe
        echo 2. Se funcionar, compacte a pasta dist\MiniPcCapture\ para distribuição
        echo 3. O software funcionará em qualquer Windows sem precisar instalar Python!
        echo.
        
        :: Perguntar se quer abrir a pasta
        set /p open=Deseja abrir a pasta do executável? (s/n): 
        if /i "%open%"=="s" (
            explorer "dist\MiniPcCapture"
        )
        
        :: Perguntar se quer testar
        set /p test=Deseja testar o executável agora? (s/n): 
        if /i "%test%"=="s" (
            cd "dist\MiniPcCapture"
            MiniPcCapture.exe
        )
        
    ) else (
        echo ❌ ERRO: Executável não foi criado!
        echo Verifique os erros acima.
    )
) else (
    echo.
    echo ==========================================
    echo   ❌ ERRO NA COMPILAÇÃO
    echo ==========================================
    echo.
    echo Verifique os erros acima e tente novamente.
    echo.
    echo DICAS:
    echo - Certifique-se de que main.py está na pasta atual
    echo - Verifique se platform-tools existe
    echo - Tente executar: pip install --upgrade pyinstaller
)

echo.
pause 