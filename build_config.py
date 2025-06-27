"""
Configuração para compilação com Auto-PY-to-EXE
Execute este arquivo para gerar automaticamente o executável
"""

import subprocess
import sys
import os

def build_executable():
    """
    Compila o executável usando PyInstaller com as configurações corretas
    """
    
    # Verificar se PyInstaller está instalado
    try:
        import PyInstaller
        print("✓ PyInstaller encontrado")
    except ImportError:
        print("❌ PyInstaller não encontrado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Comando PyInstaller
    cmd = [
        "pyinstaller",
        "--onedir",                    # Criar pasta com executável
        "--windowed",                  # Sem console (GUI only)
        "--name", "MiniPcCapture",     # Nome do executável
        "--icon", "icon.ico" if os.path.exists("icon.ico") else None,  # Ícone (se existir)
        "--add-data", "platform-tools;platform-tools",  # Incluir pasta platform-tools
        "--distpath", "dist",          # Pasta de saída
        "--workpath", "build",         # Pasta de trabalho
        "--specpath", ".",             # Pasta do spec
        "main.py"                      # Arquivo principal
    ]
    
    # Remover None do comando
    cmd = [item for item in cmd if item is not None]
    
    print("🔧 Compilando executável...")
    print(f"Comando: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ Compilação concluída com sucesso!")
        print(f"📁 Executável criado em: dist/MiniPcCapture/")
        print("📋 Arquivo principal: MiniPcCapture.exe")
        
        # Verificar se executável foi criado
        exe_path = "dist/MiniPcCapture/MiniPcCapture.exe"
        if os.path.exists(exe_path):
            print(f"✓ Executável confirmado: {exe_path}")
            
            # Verificar se platform-tools foi incluído
            platform_tools_path = "dist/MiniPcCapture/platform-tools"
            if os.path.exists(platform_tools_path):
                print("✓ Platform-tools incluído corretamente")
            else:
                print("⚠ AVISO: Platform-tools pode não ter sido incluído")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro na compilação: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("  COMPILADOR - MiniPc Capture")
    print("=" * 50)
    
    # Verificar arquivos necessários
    if not os.path.exists("main.py"):
        print("❌ Arquivo main.py não encontrado!")
        sys.exit(1)
    
    if not os.path.exists("platform-tools"):
        print("❌ Pasta platform-tools não encontrada!")
        print("   Certifique-se de que a pasta platform-tools está no diretório atual")
        sys.exit(1)
    
    print("✓ Arquivos necessários encontrados")
    
    # Perguntar se quer prosseguir
    response = input("\nDeseja compilar o executável? (s/n): ")
    if response.lower() == 's':
        success = build_executable()
        if success:
            print("\n🎉 SUCESSO! Executável pronto para distribuição!")
            print("\n📋 INSTRUÇÕES:")
            print("1. Copie toda a pasta 'dist/MiniPcCapture/' para onde quiser")
            print("2. Execute 'MiniPcCapture.exe' na pasta copiada")
            print("3. O ADB já está incluído, não precisa instalar nada!")
        else:
            print("\n❌ Falha na compilação. Verifique os erros acima.")
    else:
        print("Compilação cancelada.") 