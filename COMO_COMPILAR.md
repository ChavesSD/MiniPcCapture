# 📦 Como Compilar o Screnoid

Este guia explica como gerar um executável standalone do **Screnoid** que funciona sem precisar instalar Python ou ADB no computador de destino.

## 🎯 Resultado Final

Após a compilação você terá:
- **Executável único**: `Screnoid.exe`
- **ADB integrado**: Pasta `platform-tools` incluída automaticamente
- **Funcionamento offline**: Não precisa de internet ou instalações adicionais
- **Compatibilidade**: Funciona em qualquer Windows 10/11

---

## 🚀 Método 1: Script Automático (Recomendado)

### Requisitos
- Python 3.8 ou superior instalado
- Auto Py To Exe (na pasta `auto-py-to-exe` do projeto)
- Pasta `platform-tools` com ADB

### Compilar
```bash
# Execute o script de compilação
.\compilar.bat
```

O script irá:
1. ✓ Verificar requisitos
2. ✓ Criar configuração automática
3. ✓ Abrir interface do Auto Py To Exe
4. ✓ Validar resultado

**✅ Vantagens:**
- ✓ Interface visual amigável
- ✓ Configuração automática
- ✓ Fácil de usar
- ✓ Validação do resultado

---

## 📋 Instruções Detalhadas

### 1. Preparação
- Certifique-se de que Python está instalado
- Tenha a pasta `platform-tools` no projeto
- Verifique se `auto-py-to-exe.exe` está na pasta `auto-py-to-exe`

### 2. Compilação
1. Execute `compilar.bat`
2. A interface do Auto Py To Exe abrirá
3. A configuração será carregada automaticamente
4. Clique em "CONVERT .PY TO .EXE"
5. Aguarde a compilação terminar

### 3. Resultado
- O executável será criado em `dist/MiniPcCapture/`
- Copie toda a pasta para distribuir
- O executável precisa estar junto com suas dependências

---

## ⚙️ Configurações Utilizadas

O script configura automaticamente:
- Modo pasta única (não one-file)
- Interface gráfica (sem console)
- Nome: MiniPcCapture
- Inclusão do ADB
- Importações necessárias
- Limpeza de compilações anteriores

---

## 🔧 Resolução de Problemas

### Executável não inicia
- Verifique se todas as DLLs estão presentes
- Certifique-se de copiar a pasta inteira
- Teste em uma pasta sem espaços no caminho

### Erro na compilação
- Verifique o log de compilação
- Certifique-se de que todas as dependências estão instaladas
- Tente executar o Python diretamente antes de compilar

### ADB não funciona
- Verifique se platform-tools foi copiado
- Teste o ADB antes da compilação
- Certifique-se de que não há outro ADB rodando 