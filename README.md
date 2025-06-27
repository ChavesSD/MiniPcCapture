# 📱 MiniPc Capture

> **Gravação de Tela Profissional para Mini PCs Android**

Uma aplicação desktop moderna e intuitiva para gravar a tela de mini PCs Android via ADB, com interface gráfica amigável e ADB integrado.

![Badge](https://img.shields.io/badge/Versão-1.0.0-blue)
![Badge](https://img.shields.io/badge/Python-3.8+-green)
![Badge](https://img.shields.io/badge/Platform-Windows-lightgrey)
![Badge](https://img.shields.io/badge/License-MIT-orange)

## 🎯 Características Principais

### 📺 **Gravação Profissional**
- ✅ Gravação em **MP4** com qualidade ajustável
- ✅ Resolução customizável (Auto, 1080p, 720p, 480p, 360p)
- ✅ Bitrate configurável (1-20 Mbps)
- ✅ FPS ajustável (15, 24, 30, 60)
- ✅ Timer visual em tempo real

### 🖥️ **Interface Moderna**
- ✅ Design moderno com emojis e cores
- ✅ Detecção automática de dispositivos
- ✅ Log colorido de atividades
- ✅ Configurações persistentes
- ✅ Interface responsiva com scroll

### 🔧 **ADB Integrado**
- ✅ ADB local incluído (sem instalação)
- ✅ Detecção automática de dispositivos Android
- ✅ Comandos otimizados para mini PCs
- ✅ Fallback para ADB do sistema

### 📷 **Recursos Extras**
- ✅ Captura de screenshots instantânea
- ✅ Teste rápido de 10 segundos
- ✅ Verificação de espaço no dispositivo
- ✅ Pasta de saída configurável

## 📋 Pré-requisitos

### 1. Python 3.7 ou superior
```bash
python --version
```

### 2. ADB (Android Debug Bridge)
**✅ ADB JÁ INCLUÍDO** - A pasta `platform-tools` contém o ADB necessário!

*Opcional - apenas se ADB local não funcionar:*
- **Windows**: Baixar [Platform Tools](https://developer.android.com/studio/releases/platform-tools)
- **Linux**: `sudo apt install adb` ou `sudo pacman -S android-tools`
- **macOS**: `brew install android-platform-tools`

### 3. Configuração do Dispositivo Android
No seu mini PC Android:
1. Ir em **Configurações** → **Sobre**
2. Tocar 7 vezes em **Número da versão** para ativar modo desenvolvedor
3. Ir em **Configurações** → **Opções do desenvolvedor**
4. Ativar **Depuração USB**
5. Conectar via USB ou configurar ADB via Wi-Fi

## 🔧 Instalação

### 1. Executar instalação automática
```bash
# Windows - Execute o instalador
install.bat
```

### 2. Ou instalação manual
```bash
# Instalar dependências (opcional)
pip install -r requirements.txt

# Verificar se ADB local existe
dir platform-tools\adb.exe  # Windows
ls platform-tools/adb       # Linux/Mac
```

## 🖥️ Como usar

### 1. Executar o software
```bash
# Modo fácil (Windows)
executar.bat

# Ou diretamente
python main.py
```

### 2. Conectar dispositivo
- Conecte o mini PC Android via USB
- Ou configure ADB via Wi-Fi (veja seção abaixo)
- Clique em **"Atualizar Dispositivos"**

### 3. Configurar gravação
- **Resolução**: Escolha a qualidade desejada
- **Bitrate**: Taxa de bits (maior = melhor qualidade)
- **FPS**: Frames por segundo
- **Pasta de Saída**: Onde salvar os vídeos

### 4. Gravar
- Clique em **"🔴 Iniciar Gravação"**
- O timer mostrará o tempo decorrido
- Clique em **"⏹️ Parar Gravação"** para finalizar

## 📶 Conexão ADB via Wi-Fi

### Método 1: Primeira conexão USB
```bash
# 1. Conectar via USB primeiro
adb devices

# 2. Ativar ADB via Wi-Fi (substitua a porta se necessário)
adb tcpip 5555

# 3. Descobrir IP do dispositivo
adb shell ip addr show wlan0

# 4. Conectar via Wi-Fi (substitua pelo IP do dispositivo)
adb connect 192.168.1.100:5555

# 5. Desconectar USB e verificar
adb devices
```

### Método 2: Usando App (Android 11+)
1. Nas **Opções do desenvolvedor**
2. Ativar **Depuração via Wi-Fi**
3. Usar o código QR ou IP:porta mostrado

## 🔧 Resolução de Problemas

### Dispositivo não detectado
```bash
# Verificar se ADB está funcionando
adb devices

# Se vazio, verificar:
# 1. Cabo USB funcionando
# 2. Depuração USB ativada
# 3. Autorizar computador no dispositivo
```

### Erro de permissão
```bash
# No Linux, adicionar usuário ao grupo
sudo usermod -a -G plugdev $USER

# Ou executar como root (não recomendado)
sudo adb devices
```

### Gravação não inicia
- Verificar espaço em disco no dispositivo
- Tentar resolução menor
- Verificar se outro app não está usando a tela

## 📁 Estrutura de Arquivos

```
Gravar Tela MiniPC/
├── main.py              # Aplicação principal
├── adb_utils.py         # Utilitários ADB
├── requirements.txt     # Dependências
├── install.bat          # Instalador automático
├── executar.bat         # Executar facilmente
├── README.md           # Este arquivo
├── settings.json       # Configurações (criado automaticamente)
├── platform-tools/     # ADB incluído (Windows/Linux/Mac)
│   ├── adb.exe         # Executável ADB (Windows)
│   └── ...             # Outras ferramentas
└── AndroidRecordings/  # Pasta padrão de gravações
```

## ⚙️ Configurações Avançadas

### Comando ADB manual
```bash
# Gravar por 30 segundos em 720p
adb shell screenrecord --size 1280x720 --bit-rate 8000000 --time-limit 30 /sdcard/screen.mp4

# Baixar arquivo
adb pull /sdcard/screen.mp4 ./gravacao.mp4

# Remover do dispositivo
adb shell rm /sdcard/screen.mp4
```

### Personalizações no código
- Modificar resoluções disponíveis na linha 67
- Alterar bitrates máximos na linha 75
- Configurar pasta padrão na linha 20

## 🔒 Segurança

- **Depuração USB**: Desative quando não estiver usando
- **ADB via Wi-Fi**: Desconecte após uso para evitar acesso não autorizado
- **Autorização**: Sempre verifique o computador antes de autorizar

## 📱 Dispositivos Testados

- ✅ Mini PC Android TV Box
- ✅ Tablets Android
- ✅ Smartphones Android
- ✅ Emuladores Android (BlueStacks, etc.)

## 🐛 Relatórios de Bug

Para reportar problemas:
1. Verificar o log de atividades no software
2. Testar comandos ADB manualmente
3. Incluir informações do sistema e dispositivo

## 👨‍💻 Créditos

**Desenvolvido por**: Deyvison Chaves  
**Versão**: 1.0.0  
**Tecnologia**: Python + Tkinter + ADB  

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

---

**🎉 Divirta-se gravando suas telas com qualidade profissional!** 