"""
Configuração para compilação com Auto-PY-to-EXE
Execute este arquivo para gerar automaticamente o executável
"""

import subprocess
import sys
import os
import shutil

def get_pyinstaller_args():
    """Retorna os argumentos para o PyInstaller"""
    return [
        "main.py",                   # Arquivo principal
        "--onedir",                  # Criar pasta com arquivos
        "--windowed",               # Sem console
        "--clean",                  # Limpar cache
        "--name", "Screnoid",     # Nome do executável
        "--icon=icon.ico",         # Ícone do executável
        "--add-data", "platform-tools;platform-tools",  # Incluir ADB
        "--hidden-import", "PIL._tkinter_finder",  # Fix Pillow
    ]

def main():
    """Função principal de compilação"""
    try:
        # Limpar diretório dist
        if os.path.exists("dist"):
            shutil.rmtree("dist")
        
        # Criar arquivo de configuração
        create_config_file()
        
        # Executar auto-py-to-exe
        subprocess.run(["auto-py-to-exe", "-c", "auto-py-to-exe-config.json"])
        
        # Verificar se compilou
        print("\n✅ Compilação concluída!")
        print(f"📁 Executável criado em: dist/Screnoid/")
        print("📋 Arquivo principal: Screnoid.exe")
        
        # Verificar arquivos
        exe_path = "dist/Screnoid/Screnoid.exe"
        if not os.path.exists(exe_path):
            raise Exception("Executável não foi criado!")
            
        # Verificar ADB
        platform_tools_path = "dist/Screnoid/platform-tools"
        if not os.path.exists(platform_tools_path):
            raise Exception("ADB não foi incluído!")
            
        print("\n✨ Tudo certo! O executável está pronto para uso.")
        
    except Exception as e:
        print(f"\n❌ Erro na compilação: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Header
    print("\n" + "="*50)
    print("  COMPILADOR - Screnoid")
    print("="*50 + "\n")
    
    # Verificar Python
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 ou superior é necessário!")
        sys.exit(1)
    
    # Executar
    main()
    
    # Instruções finais
    print("\n📋 Para distribuir:")
    print("1. Copie toda a pasta 'dist/Screnoid/' para onde quiser")
    print("2. Execute 'Screnoid.exe' na pasta copiada")
    print("\n✨ Pronto! Bom uso!\n") 