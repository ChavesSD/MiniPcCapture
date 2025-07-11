import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading
import os
import time
from datetime import datetime
import json
import sys
import io
from PIL import Image, ImageTk
import ctypes
import win32api
import win32con
import socket
import requests
from ctypes import windll, Structure, c_long, byref, c_int, c_ulong, POINTER, sizeof, c_ushort, c_short

# Estruturas para configuração de monitor
class POINTL(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]

class DEVMODE(Structure):
    _fields_ = [
        ('dmDeviceName', c_int * 32),
        ('dmSpecVersion', c_ushort),
        ('dmDriverVersion', c_ushort),
        ('dmSize', c_ushort),
        ('dmDriverExtra', c_ushort),
        ('dmFields', c_ulong),
        ('union1', POINTL),
        ('dmColor', c_short),
        ('dmDuplex', c_short),
        ('dmYResolution', c_short),
        ('dmTTOption', c_short),
        ('dmCollate', c_short),
        ('dmFormName', c_int * 32),
        ('dmLogPixels', c_ushort),
        ('dmBitsPerPel', c_ulong),
        ('dmPelsWidth', c_ulong),
        ('dmPelsHeight', c_ulong),
        ('dmDisplayFlags', c_ulong),
        ('dmDisplayFrequency', c_ulong),
        ('dmICMMethod', c_ulong),
        ('dmICMIntent', c_ulong),
        ('dmMediaType', c_ulong),
        ('dmDitherType', c_ulong),
        ('dmReserved1', c_ulong),
        ('dmReserved2', c_ulong),
        ('dmPanningWidth', c_ulong),
        ('dmPanningHeight', c_ulong),
    ]

def is_admin():
    """Verifica se o programa está rodando como administrador"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def setup_virtual_monitor():
    """Configura o monitor virtual usando o driver USBMMIDD"""
    if not is_admin():
        messagebox.showerror("Erro", "Este programa precisa ser executado como Administrador para configurar o monitor virtual.")
        return False
        
    try:
        # Caminho para o diretório do driver
        driver_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "usbmmidd_v2")
        
        # Determina qual versão do instalador usar (32 ou 64 bits)
        installer = "deviceinstaller64.exe" if sys.maxsize > 2**32 else "deviceinstaller.exe"
        installer_path = os.path.join(driver_dir, installer)
        
        # Primeiro, tenta remover qualquer instalação anterior
        subprocess.run(f'"{installer_path}" stop usbmmidd', 
                      cwd=driver_dir, capture_output=True, text=True, shell=True)
        subprocess.run(f'"{installer_path}" remove usbmmidd', 
                      cwd=driver_dir, capture_output=True, text=True, shell=True)
        
        # Instala o driver
        install_cmd = f'"{installer_path}" install usbmmidd.inf usbmmidd'
        result = subprocess.run(install_cmd, cwd=driver_dir, capture_output=True, text=True, shell=True)
        
        if result.returncode != 0 and "already installed" not in result.stdout.lower():
            raise Exception(f"Erro ao instalar driver: {result.stdout}\n{result.stderr}")
        
        # Desativa qualquer monitor virtual existente
        disable_cmd = f'"{installer_path}" enableidd 0'
        subprocess.run(disable_cmd, cwd=driver_dir, capture_output=True, text=True, shell=True)
        time.sleep(2)  # Aguarda a desativação
        
        # Ativa o monitor virtual
        enable_cmd = f'"{installer_path}" enableidd 1'
        result = subprocess.run(enable_cmd, cwd=driver_dir, capture_output=True, text=True, shell=True)
        
        if result.returncode != 0:
            raise Exception(f"Erro ao ativar monitor: {result.stdout}\n{result.stderr}")
        
        # Aguarda o Windows detectar o novo monitor
        time.sleep(3)
        
        # Configura o modo de exibição estendido
        try:
            # Obtém informações dos monitores
            device0 = win32api.EnumDisplayDevices(None, 0, 0)  # Monitor principal
            device1 = win32api.EnumDisplayDevices(None, 1, 0)  # Monitor virtual
            
            if not device1:
                raise Exception("Monitor virtual não detectado")
                
            settings0 = win32api.EnumDisplaySettings(device0.DeviceName, win32con.ENUM_CURRENT_SETTINGS)
            settings1 = win32api.EnumDisplaySettings(device1.DeviceName, win32con.ENUM_CURRENT_SETTINGS)
            
            # Configura o monitor principal
            devmode0 = DEVMODE()
            devmode0.dmSize = sizeof(DEVMODE)
            devmode0.dmDriverExtra = 0
            devmode0.dmFields = (win32con.DM_POSITION | win32con.DM_PELSWIDTH | 
                               win32con.DM_PELSHEIGHT | win32con.DM_BITSPERPEL)
            devmode0.dmPelsWidth = settings0.PelsWidth
            devmode0.dmPelsHeight = settings0.PelsHeight
            devmode0.dmBitsPerPel = settings0.BitsPerPel
            devmode0.union1.x = 0
            devmode0.union1.y = 0
            
            # Aplica configurações ao monitor principal
            result = windll.user32.ChangeDisplaySettingsExW(
                device0.DeviceName,
                byref(devmode0),
                None,
                win32con.CDS_UPDATEREGISTRY | win32con.CDS_NORESET,
                None
            )
            
            if result != win32con.DISP_CHANGE_SUCCESSFUL:
                print(f"Aviso: Erro ao configurar monitor principal: {result}")
            
            time.sleep(1)
            
            # Configura o monitor virtual
            devmode1 = DEVMODE()
            devmode1.dmSize = sizeof(DEVMODE)
            devmode1.dmDriverExtra = 0
            devmode1.dmFields = (win32con.DM_POSITION | win32con.DM_PELSWIDTH | 
                               win32con.DM_PELSHEIGHT | win32con.DM_BITSPERPEL)
            devmode1.dmPelsWidth = 1920
            devmode1.dmPelsHeight = 1080
            devmode1.dmBitsPerPel = settings0.BitsPerPel
            devmode1.union1.x = settings0.PelsWidth  # Posiciona à direita do monitor principal
            devmode1.union1.y = 0
            
            # Aplica configurações ao monitor virtual
            result = windll.user32.ChangeDisplaySettingsExW(
                device1.DeviceName,
                byref(devmode1),
                None,
                win32con.CDS_UPDATEREGISTRY | win32con.CDS_NORESET,
                None
            )
            
            if result != win32con.DISP_CHANGE_SUCCESSFUL:
                raise Exception(f"Erro ao configurar monitor virtual: {result}")
            
            # Aplica todas as mudanças
            result = windll.user32.ChangeDisplaySettingsW(None, 0)
            if result != win32con.DISP_CHANGE_SUCCESSFUL:
                raise Exception(f"Erro ao aplicar mudanças: {result}")
            
            # Aguarda as configurações serem aplicadas
            time.sleep(2)
            
            # Mostra mensagem para o usuário
            messagebox.showinfo("Configuração de Monitor", 
                "Monitor virtual configurado!\n\n"
                "Para ajustar o modo de exibição:\n\n"
                "1. Pressione Windows + P\n"
                "2. Selecione uma das opções:\n"
                "   - PC Screen only: Apenas monitor principal\n"
                "   - Duplicate: Duplicar telas\n"
                "   - Extend: Estender telas (recomendado)\n"
                "   - Second screen only: Apenas segunda tela\n\n"
                "3. Aguarde alguns segundos para o Windows aplicar a configuração")
            
        except Exception as e:
            print(f"Aviso: Erro ao configurar modo de exibição: {e}")
            # Continua mesmo com erro, pois algumas configurações podem ter funcionado
        
        return True
        
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao configurar monitor virtual:\n{str(e)}")
        return False

def disable_virtual_monitor():
    """Desativa o monitor virtual"""
    try:
        driver_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "usbmmidd_v2")
        installer = "deviceinstaller64.exe" if sys.maxsize > 2**32 else "deviceinstaller.exe"
        installer_path = os.path.join(driver_dir, installer)
        
        # Desativa o monitor
        disable_cmd = f'"{installer_path}" enableidd 0'
        subprocess.run(disable_cmd, cwd=driver_dir, capture_output=True, text=True, shell=True)
        time.sleep(2)  # Aguarda a desativação
        
        # Remove o driver
        subprocess.run(f'"{installer_path}" stop usbmmidd', 
                      cwd=driver_dir, capture_output=True, text=True, shell=True)
        subprocess.run(f'"{installer_path}" remove usbmmidd', 
                      cwd=driver_dir, capture_output=True, text=True, shell=True)
        
    except Exception as e:
        print(f"Erro ao desativar monitor virtual: {e}")

# Informações da aplicação
APP_NAME = "Screnoid"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Deyvison Chaves"

class AndroidScreenRecorder:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("750x650")
        self.root.minsize(750, 650)
        self.root.resizable(False, False)  # Impedir redimensionamento
        
        # Configurar ícone da janela (se existir)
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass  # Ignorar se não encontrar ícone
        
        # Configurar tema moderno
        self.setup_modern_theme()
        
        # Configurar caminho do ADB local
        self.setup_adb_path()
        
        # Variáveis de controle
        self.is_recording = False
        self.is_mirroring = False
        self.connected_device = None
        self.recording_process = None
        self.mirroring_process = None
        self.output_folder = os.path.expanduser("~/Desktop/Screnoid")
        
        # Criar pasta de saída se não existir
        os.makedirs(self.output_folder, exist_ok=True)
        
        # Carregar configurações
        self.load_settings()
        
        # Criar interface
        self.create_widgets()
        
        # Verificar ADB na inicialização
        self.check_adb_connection()
    
    def setup_modern_theme(self):
        """Configura tema moderno e cores"""
        style = ttk.Style()
        
        # Tentar tema moderno se disponível
        available_themes = style.theme_names()
        if "vista" in available_themes:
            style.theme_use("vista")
        elif "clam" in available_themes:
            style.theme_use("clam")
        elif "alt" in available_themes:
            style.theme_use("alt")
        
        # Configurar cores personalizadas
        style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"), foreground="#2E86AB")
        style.configure("Footer.TLabel", font=("Segoe UI", 8), foreground="#666666")
        style.configure("Success.TLabel", foreground="#059862")
        style.configure("Warning.TLabel", foreground="#F18F01")
        style.configure("Error.TLabel", foreground="#C73E1D")
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))
        
        # Configurar fundo da janela
        self.root.configure(bg="#F5F5F5")
    
    def setup_adb_path(self):
        """Configura o caminho para o ADB local"""
        # Determinar o diretório base (funciona tanto no script quanto no executável)
        if getattr(sys, 'frozen', False):
            # Executando como executável PyInstaller
            base_dir = sys._MEIPASS
        else:
            # Executando como script Python
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Caminho para platform-tools
        platform_tools_dir = os.path.join(base_dir, "platform-tools")
        
        # Determinar o executável ADB baseado no OS
        if os.name == 'nt':  # Windows
            self.adb_path = os.path.join(platform_tools_dir, "adb.exe")
        else:  # Linux/Mac
            self.adb_path = os.path.join(platform_tools_dir, "adb")
        
        # Verificar se o arquivo existe
        if not os.path.exists(self.adb_path):
            # Fallback para ADB do sistema
            self.adb_path = "adb"
            self.using_local_adb = False
        else:
            self.using_local_adb = True
    
    def get_adb_command(self, *args):
        """Retorna comando ADB completo com argumentos"""
        return [self.adb_path] + list(args)
    
    def create_widgets(self):
        # === CONTAINER PRINCIPAL SEM SCROLL ===
        main_container = ttk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # === HEADER DA APLICAÇÃO ===
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill="x", pady=(5, 10))
        
        # Título principal
        title_label = ttk.Label(header_frame, text=APP_NAME, style="Header.TLabel")
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, text="Gravação de Tela e Segunda Tela para Mini PCs Android", 
                                  font=("Segoe UI", 9), foreground="#666666")
        subtitle_label.pack(pady=(2, 0))
        
        # Separador
        ttk.Separator(main_container, orient="horizontal").pack(fill="x", pady=(0, 10))
        
        # === SEÇÃO DE CONEXÃO ===
        connection_frame = ttk.LabelFrame(main_container, text="🔗 Conexão com Dispositivo", padding="8")
        connection_frame.pack(fill="x", pady=(0, 8))
        connection_frame.columnconfigure(1, weight=1)
        
        # Status com ícones
        ttk.Label(connection_frame, text="Status:", font=("Segoe UI", 8, "bold")).grid(row=0, column=0, sticky=tk.W, padx=(0, 8))
        self.status_label = ttk.Label(connection_frame, text="🔍 Verificando...", foreground="#F18F01", font=("Segoe UI", 8))
        self.status_label.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Button(connection_frame, text="🔄 Atualizar", 
                  command=self.refresh_devices).grid(row=0, column=2, padx=(10, 0))
        
        # Dispositivo
        ttk.Label(connection_frame, text="Dispositivo:", font=("Segoe UI", 8, "bold")).grid(row=1, column=0, sticky=tk.W, padx=(0, 8), pady=(8, 0))
        self.device_combo = ttk.Combobox(connection_frame, state="readonly", font=("Segoe UI", 8))
        self.device_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(8, 0))
        self.device_combo.bind('<<ComboboxSelected>>', self.on_device_selected)
        
        # Status do ADB
        adb_status = "📱 Local" if self.using_local_adb else "💻 Sistema"
        self.adb_status_label = ttk.Label(connection_frame, text=adb_status, font=("Segoe UI", 7))
        self.adb_status_label.grid(row=1, column=2, padx=(10, 0), pady=(8, 0))
        
        # === NOTEBOOK PARA ABAS ===
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill="both", expand=True, pady=(0, 8))

        # === ABA DE GRAVAÇÃO ===
        recording_frame = ttk.Frame(self.notebook)
        self.notebook.add(recording_frame, text="📹 Gravação")
        self.create_recording_tab(recording_frame)

        # === ABA DE SEGUNDA TELA ===
        mirroring_frame = ttk.Frame(self.notebook)
        self.notebook.add(mirroring_frame, text="🖥️ Segunda Tela")
        self.create_mirroring_tab(mirroring_frame)

    def create_recording_tab(self, parent):
        # === SEÇÃO DE CONFIGURAÇÕES ===
        settings_frame = ttk.LabelFrame(parent, text="⚙️ Configurações de Gravação", padding="8")
        settings_frame.pack(fill="x", pady=(0, 8))
        settings_frame.columnconfigure(1, weight=1)
        
        # Linha 1: Resolução e Bitrate
        ttk.Label(settings_frame, text="Resolução:", font=("Segoe UI", 8)).grid(row=0, column=0, sticky=tk.W, padx=(0, 8))
        self.resolution_var = tk.StringVar(value="1920x1080")
        resolution_combo = ttk.Combobox(settings_frame, textvariable=self.resolution_var,
                                       values=["1920x1080", "1280x720", "854x480", "640x360", "Auto"],
                                       font=("Segoe UI", 8), width=12)
        resolution_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 15))
        
        ttk.Label(settings_frame, text="Bitrate:", font=("Segoe UI", 8)).grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.bitrate_var = tk.StringVar(value="8")
        bitrate_spin = ttk.Spinbox(settings_frame, from_=1, to=20, textvariable=self.bitrate_var, width=6, font=("Segoe UI", 8))
        bitrate_spin.grid(row=0, column=3, sticky=tk.W)
        
        # Linha 2: FPS e Tempo
        ttk.Label(settings_frame, text="FPS:", font=("Segoe UI", 8)).grid(row=1, column=0, sticky=tk.W, padx=(0, 8), pady=(8, 0))
        self.fps_var = tk.StringVar(value="30")
        fps_combo = ttk.Combobox(settings_frame, textvariable=self.fps_var,
                                values=["15", "24", "30", "60"],
                                font=("Segoe UI", 8), width=12)
        fps_combo.grid(row=1, column=1, sticky=tk.W, pady=(8, 0))
        
        ttk.Label(settings_frame, text="Tempo Máx (min):", font=("Segoe UI", 8)).grid(row=1, column=2, sticky=tk.W, padx=(0, 5), pady=(8, 0))
        self.max_time_var = tk.StringVar(value="3")
        max_time_spin = ttk.Spinbox(settings_frame, from_=1, to=180, textvariable=self.max_time_var, width=6, font=("Segoe UI", 8))
        max_time_spin.grid(row=1, column=3, sticky=tk.W, pady=(8, 0))
        
        # Linha 3: Pasta de Saída
        ttk.Label(settings_frame, text="Pasta Saída:", font=("Segoe UI", 8)).grid(row=2, column=0, sticky=tk.W, padx=(0, 8), pady=(8, 0))
        self.output_path_var = tk.StringVar(value=self.output_folder)
        output_entry = ttk.Entry(settings_frame, textvariable=self.output_path_var, font=("Segoe UI", 8))
        output_entry.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(8, 0))
        
        ttk.Button(settings_frame, text="📁", width=3, 
                  command=self.choose_output_folder).grid(row=2, column=3, sticky=tk.W, pady=(8, 0))
        
        # === SEÇÃO DE CONTROLE ===
        control_frame = ttk.LabelFrame(parent, text="🎮 Controles", padding="8")
        control_frame.pack(fill="x", pady=(0, 8))
        control_frame.columnconfigure(1, weight=1)
        
        # Botões principais
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        self.record_button = ttk.Button(button_frame, text="🔴 Iniciar Gravação", 
                                       command=self.toggle_recording, style="Accent.TButton")
        self.record_button.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        self.screenshot_button = ttk.Button(button_frame, text="📷 Screenshot", 
                                           command=self.take_screenshot)
        self.screenshot_button.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Botão de teste
        self.test_button = ttk.Button(control_frame, text="🧪 Teste (10s)", 
                                     command=self.test_recording)
        self.test_button.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Timer de gravação
        self.time_label = ttk.Label(control_frame, text="⏱️ Tempo: 00:00:00", font=("Segoe UI", 11, "bold"))
        self.time_label.grid(row=2, column=0, columnspan=2, pady=(8, 0))
        
        # === SEÇÃO DE LOG COMPACTA ===
        log_frame = ttk.LabelFrame(parent, text="📋 Log", padding="8")
        log_frame.pack(fill="both", expand=True, pady=(0, 8))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Log com cores
        self.log_text = scrolledtext.ScrolledText(log_frame, height=4, wrap=tk.WORD, 
                                                 font=("Consolas", 8), bg="#FAFAFA")
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar tags para cores no log
        self.log_text.tag_configure("success", foreground="#059862")
        self.log_text.tag_configure("error", foreground="#D73A49")
        self.log_text.tag_configure("warning", foreground="#F18F01")
        self.log_text.tag_configure("info", foreground="#0366D6")

    def create_mirroring_tab(self, parent):
        """Cria a aba de segunda tela"""
        # === SEÇÃO DE CONFIGURAÇÕES DE SEGUNDA TELA ===
        settings_frame = ttk.LabelFrame(parent, text="⚙️ Configurações de Segunda Tela", padding="8")
        settings_frame.pack(fill="x", pady=(0, 8))
        settings_frame.columnconfigure(1, weight=1)
        
        # Linha 1: Resolução e FPS
        ttk.Label(settings_frame, text="Resolução:", font=("Segoe UI", 8)).grid(row=0, column=0, sticky=tk.W, padx=(0, 8))
        self.resolution_var = tk.StringVar(value="1920x1080")
        self.resolution_combo = ttk.Combobox(settings_frame, textvariable=self.resolution_var,
                                           values=["1920x1080", "1280x720", "854x480"],
                                           font=("Segoe UI", 8), width=12)
        self.resolution_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 15))
        
        ttk.Label(settings_frame, text="FPS:", font=("Segoe UI", 8)).grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.fps_var = tk.StringVar(value="30")
        self.fps_combo = ttk.Combobox(settings_frame, textvariable=self.fps_var,
                                     values=["15", "30", "60"],
                                     font=("Segoe UI", 8), width=6)
        self.fps_combo.grid(row=0, column=3, sticky=tk.W)
        
        # Linha 2: Monitor
        ttk.Label(settings_frame, text="Monitor:", font=("Segoe UI", 8)).grid(row=1, column=0, sticky=tk.W, padx=(0, 8), pady=(8, 0))
        self.monitor_var = tk.StringVar(value="Principal")
        self.monitor_combo = ttk.Combobox(settings_frame, textvariable=self.monitor_var,
                                        values=["Principal", "Secundário"],
                                        font=("Segoe UI", 8), width=12)
        self.monitor_combo.grid(row=1, column=1, sticky=tk.W, pady=(8, 0))
        
        # === SEÇÃO DE CONTROLES ===
        control_frame = ttk.LabelFrame(parent, text="🎮 Controles", padding="8")
        control_frame.pack(fill="x", pady=(0, 8))
        
        # Botão de iniciar/parar
        self.mirror_button = ttk.Button(control_frame, text="🖥️ Iniciar Segunda Tela",
                                      command=self.toggle_mirroring, style="Accent.TButton")
        self.mirror_button.pack(fill="x")
        
        # === SEÇÃO DE INSTRUÇÕES ===
        instructions_frame = ttk.LabelFrame(parent, text="📋 Instruções", padding="8")
        instructions_frame.pack(fill="both", expand=True)
        
        # Texto de instruções
        self.instructions_text = scrolledtext.ScrolledText(instructions_frame, wrap=tk.WORD,
                                                         font=("Segoe UI", 9), height=8)
        self.instructions_text.pack(fill="both", expand=True)
        
        # Atualizar instruções iniciais
        self.update_instructions()

    def update_instructions(self):
        """Atualiza as instruções para a segunda tela"""
        self.instructions_text.configure(state="normal")
        self.instructions_text.delete(1.0, tk.END)
        
        monitor = self.monitor_var.get()
        if monitor == "Principal":
            instructions = """Para usar a segunda tela (Monitor Principal):
1. Selecione 'Principal' como monitor
2. Clique em 'Iniciar Segunda Tela'
3. No dispositivo Android, abra o navegador
4. Acesse o endereço IP que aparecerá na tela

Dicas:
- Mantenha o dispositivo Android conectado à energia
- Use rede Wi-Fi 5GHz se disponível
- Ajuste a resolução/FPS conforme necessário"""
        else:
            instructions = """Para usar a segunda tela (Monitor Virtual):
1. Selecione 'Secundário' como monitor
2. Execute o programa como Administrador
3. Clique em 'Iniciar Segunda Tela'
4. Quando aparecer o aviso do Windows Defender, clique em 'Permitir acesso'
5. Pressione Windows + P e selecione 'Estender'
6. No dispositivo Android, abra o navegador e acesse o IP mostrado

Dicas:
- O monitor virtual permite usar o Android como uma extensão da sua tela
- Se a tela estiver duplicada, use Windows + P > Estender
- Para ajustar a posição do monitor virtual:
  * Clique direito na área de trabalho
  * Configurações de exibição
  * Arraste o monitor 2 para a posição desejada"""
        
        self.instructions_text.insert("1.0", instructions)
        self.instructions_text.configure(state="disabled")

    def toggle_mirroring(self):
        """Inicia ou para a segunda tela"""
        if not self.is_mirroring:
            self.start_mirroring()
        else:
            self.stop_mirroring()

    def start_mirroring(self):
        """Inicia o servidor de segunda tela"""
        try:
            # Configura monitor virtual se necessário
            if self.monitor_var.get() == "Secundário":
                self.log_message("Configurando monitor virtual...")
                if not setup_virtual_monitor():
                    return
                
                # Mostra instruções para configurar modo estendido
                messagebox.showinfo("Monitor Virtual", 
                    "Monitor virtual configurado!\n\n"
                    "Para garantir que a tela esteja no modo estendido:\n\n"
                    "1. Pressione Windows + P\n"
                    "2. Selecione 'Estender'\n"
                    "3. Aguarde alguns segundos para o Windows configurar o monitor")
            
            # Determina o índice do monitor
            monitor_index = 1 if self.monitor_var.get() == "Secundário" else 0
            
            # Inicia o servidor em uma thread separada
            self.server_thread = threading.Thread(
                target=self.mirroring_loop,
                args=(self.resolution_var.get(), self.fps_var.get(), monitor_index),
                daemon=True
            )
            self.server_thread.start()
            
            # Atualiza a interface
            self.is_mirroring = True
            self.mirror_button.configure(text="⏹️ Parar Segunda Tela", style="")
            self.log_message("Segunda tela iniciada!", "success")
            
        except Exception as e:
            self.log_message(f"Erro ao iniciar segunda tela: {e}", "error")
            messagebox.showerror("Erro", f"Erro ao iniciar segunda tela:\n{str(e)}")

    def mirroring_loop(self, resolution, fps, monitor_index):
        """Loop principal do servidor de segunda tela"""
        try:
            # Obtém o IP da máquina
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            # Mostra o IP para o usuário
            self.log_message(f"Acesse no navegador do Android: http://{local_ip}:5000", "info")
            
            # Inicia o servidor Flask em um processo separado
            server_script = os.path.join(os.path.dirname(__file__), "screen_server.py")
            self.server_process = subprocess.Popen(
                [sys.executable, server_script, str(monitor_index)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Aguarda o processo terminar
            while self.server_process.poll() is None:
                time.sleep(0.1)
                
            # Verifica se houve erro
            if self.server_process.returncode != 0:
                error = self.server_process.stderr.read().decode()
                self.log_message(f"Erro no servidor: {error}", "error")
                
        except Exception as e:
            self.log_message(f"Erro no loop de segunda tela: {e}", "error")
        finally:
            self.stop_mirroring()

    def stop_mirroring(self):
        """Para o servidor de segunda tela"""
        try:
            # Tenta encerrar o servidor graciosamente
            if hasattr(self, 'server_process') and self.server_process:
                try:
                    # Tenta fazer uma requisição de shutdown
                    requests.post('http://localhost:5000/shutdown', timeout=1)
                except:
                    pass
                
                # Aguarda um pouco para o servidor encerrar
                time.sleep(1)
                
                # Se ainda estiver rodando, força o encerramento
                if self.server_process.poll() is None:
                    self.server_process.terminate()
                    self.server_process.wait(timeout=5)
                
                self.server_process = None
            
            # Desativa o monitor virtual se necessário
            if self.monitor_var.get() == "Secundário":
                self.log_message("Desativando monitor virtual...")
                disable_virtual_monitor()
            
            # Atualiza a interface
            self.is_mirroring = False
            self.mirror_button.configure(text="🖥️ Iniciar Segunda Tela", style="Accent.TButton")
            self.log_message("Segunda tela encerrada!", "success")
            
        except Exception as e:
            self.log_message(f"Erro ao parar segunda tela: {e}", "error")
            messagebox.showerror("Erro", f"Erro ao parar segunda tela:\n{str(e)}")
        finally:
            # Garante que a interface seja atualizada
            self.is_mirroring = False
            self.mirror_button.configure(text="🖥️ Iniciar Segunda Tela", style="Accent.TButton")

    def log_message(self, message, msg_type="info"):
        """Adiciona mensagem ao log com timestamp e cores"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        # Determinar cor baseada no tipo ou conteúdo da mensagem
        if msg_type == "error" or "ERRO" in message or "✗" in message:
            tag = "error"
        elif msg_type == "warning" or "AVISO" in message or "⚠" in message:
            tag = "warning"
        elif msg_type == "success" or "✓" in message or "sucesso" in message.lower():
            tag = "success"
        else:
            tag = "info"
        
        self.log_text.insert(tk.END, formatted_message, tag)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """Limpa o log de atividades"""
        self.log_text.delete(1.0, tk.END)
    
    def check_adb_connection(self):
        """Verifica se ADB está disponível e atualiza lista de dispositivos"""
        try:
            result = subprocess.run(self.get_adb_command('version'), capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                adb_source = "local" if self.using_local_adb else "sistema"
                self.log_message(f"ADB {adb_source} encontrado e funcionando")
                self.refresh_devices()
            else:
                self.status_label.config(text="ADB não encontrado", foreground="red")
                self.log_message("ERRO: ADB não encontrado")
        except subprocess.TimeoutExpired:
            self.status_label.config(text="ADB timeout", foreground="red")
            self.log_message("ERRO: Timeout ao verificar ADB")
        except FileNotFoundError:
            self.status_label.config(text="ADB não instalado", foreground="red")
            self.log_message("ERRO: ADB não está instalado")
        except Exception as e:
            self.status_label.config(text="Erro ADB", foreground="red")
            self.log_message(f"ERRO: {str(e)}")
    
    def refresh_devices(self):
        """Atualiza lista de dispositivos conectados"""
        try:
            result = subprocess.run(self.get_adb_command('devices'), capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Pular primeira linha
                devices = []
                for line in lines:
                    if line.strip() and '\tdevice' in line:
                        device_id = line.split('\t')[0]
                        devices.append(device_id)
                
                self.device_combo['values'] = devices
                
                if devices:
                    if not self.connected_device or self.connected_device not in devices:
                        self.device_combo.set(devices[0])
                        self.connected_device = devices[0]
                    self.status_label.config(text=f"Conectado: {len(devices)} dispositivo(s)", foreground="green")
                    self.log_message(f"Encontrados {len(devices)} dispositivo(s)")
                else:
                    self.device_combo.set("")
                    self.connected_device = None
                    self.status_label.config(text="Nenhum dispositivo conectado", foreground="orange")
                    self.log_message("Nenhum dispositivo Android conectado")
            
        except Exception as e:
            self.status_label.config(text="Erro ao verificar dispositivos", foreground="red")
            self.log_message(f"ERRO ao verificar dispositivos: {str(e)}")
    
    def on_device_selected(self, event):
        """Callback quando dispositivo é selecionado"""
        self.connected_device = self.device_combo.get()
        self.log_message(f"Dispositivo selecionado: {self.connected_device}")
    
    def choose_output_folder(self):
        """Permite escolher pasta de saída"""
        folder = filedialog.askdirectory(initialdir=self.output_folder)
        if folder:
            self.output_folder = folder
            self.output_path_var.set(folder)
            self.log_message(f"Pasta de saída alterada para: {folder}")
    
    def toggle_recording(self):
        """Inicia ou para a gravação"""
        if not self.connected_device:
            messagebox.showerror("Erro", "Nenhum dispositivo conectado!")
            return
        
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """Inicia gravação da tela"""
        try:
            # Verificar espaço no dispositivo primeiro
            self.log_message("Verificando espaço disponível no dispositivo...")
            space_check = subprocess.run(
                self.get_adb_command('-s', self.connected_device, 'shell', 'df', '/sdcard'),
                capture_output=True, text=True, timeout=10
            )
            if space_check.returncode == 0:
                lines = space_check.stdout.strip().split('\n')
                if len(lines) > 1:
                    data = lines[1].split()
                    if len(data) >= 4:
                        available_kb = int(data[3])
                        available_mb = available_kb / 1024
                        self.log_message(f"Espaço disponível: {available_mb:.0f} MB")
                        if available_mb < 100:
                            messagebox.showwarning("Pouco Espaço", f"Apenas {available_mb:.0f} MB disponíveis no dispositivo!")
            
            # Gerar nome do arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screen_record_{timestamp}.mp4"
            self.current_file_path = os.path.join(self.output_folder, filename)
            
            # Construir comando ADB
            cmd = self.get_adb_command('-s', self.connected_device, 'shell', 'screenrecord')
            
            # Adicionar opções
            if self.resolution_var.get() != "Auto":
                cmd.extend(['--size', self.resolution_var.get()])
            
            cmd.extend(['--bit-rate', f"{int(self.bitrate_var.get())}M"])
            time_limit_seconds = int(self.max_time_var.get()) * 60  # Converter minutos para segundos
            cmd.extend(['--time-limit', str(time_limit_seconds)])
            
            # Caminho no dispositivo
            device_path = f"/sdcard/screen_record_{timestamp}.mp4"
            cmd.append(device_path)
            
            # Log do comando completo
            cmd_str = ' '.join(cmd)
            self.log_message(f"Comando: {cmd_str}")
            self.log_message(f"Arquivo no dispositivo: {device_path}")
            self.log_message(f"Arquivo local: {self.current_file_path}")
            
            # Verificar se screenrecord existe no dispositivo
            test_cmd = self.get_adb_command('-s', self.connected_device, 'shell', 'which', 'screenrecord')
            test_result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=5)
            if test_result.returncode != 0:
                self.log_message("ERRO: Comando screenrecord não encontrado no dispositivo!")
                messagebox.showerror("Erro", "O dispositivo não suporta gravação de tela (screenrecord não encontrado)")
                return
            
            # Iniciar gravação
            self.log_message("Iniciando processo de gravação...")
            self.recording_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.device_file_path = device_path
            
            # Verificar se o processo iniciou corretamente
            time.sleep(1)  # Dar tempo para iniciar
            if self.recording_process.poll() is not None:
                # Processo terminou imediatamente - erro
                stdout, stderr = self.recording_process.communicate()
                self.log_message(f"ERRO: Processo terminou imediatamente!")
                self.log_message(f"Stdout: {stdout.decode() if stdout else 'Vazio'}")
                self.log_message(f"Stderr: {stderr.decode() if stderr else 'Vazio'}")
                messagebox.showerror("Erro", "Falha ao iniciar gravação. Verifique o log para detalhes.")
                return
            
            # Atualizar interface
            self.is_recording = True
            self.record_button.config(text="⏹️ Parar Gravação", style="")
            self.start_time = time.time()
            
            # Iniciar timer
            self.update_timer()
            
            self.log_message(f"✓ Gravação iniciada com sucesso: {filename}")
            self.log_message("Processo de gravação em execução...")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao iniciar gravação: {str(e)}")
            self.log_message(f"ERRO ao iniciar gravação: {str(e)}")
    
    def stop_recording(self):
        """Para a gravação e baixa o arquivo"""
        try:
            if self.recording_process:
                self.log_message("Parando gravação...")
                
                # Parar processo de gravação
                self.recording_process.terminate()
                try:
                    self.recording_process.wait(timeout=10)
                    self.log_message("Processo de gravação finalizado")
                except subprocess.TimeoutExpired:
                    self.log_message("Forçando parada do processo...")
                    self.recording_process.kill()
                    self.recording_process.wait()
                
                # Capturar saída do processo
                try:
                    stdout, stderr = self.recording_process.communicate(timeout=5)
                    if stdout:
                        self.log_message(f"Saída do screenrecord: {stdout.decode().strip()}")
                    if stderr:
                        self.log_message(f"Erros do screenrecord: {stderr.decode().strip()}")
                except:
                    pass
                
                # Aguardar um pouco para o arquivo ser finalizado
                self.log_message("Aguardando finalização do arquivo...")
                time.sleep(3)
                
                # Verificar se arquivo foi criado no dispositivo
                self.log_message(f"Verificando se arquivo existe: {self.device_file_path}")
                check_cmd = self.get_adb_command('-s', self.connected_device, 'shell', 'ls', '-la', self.device_file_path)
                check_result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=10)
                
                if check_result.returncode == 0:
                    file_info = check_result.stdout.strip()
                    self.log_message(f"✓ Arquivo encontrado: {file_info}")
                    
                    # Extrair tamanho do arquivo
                    parts = file_info.split()
                    if len(parts) >= 5:
                        file_size = int(parts[4])
                        file_size_mb = file_size / (1024 * 1024)
                        self.log_message(f"Tamanho do arquivo: {file_size_mb:.2f} MB")
                        
                        if file_size < 1024:  # Menos de 1KB - provavelmente vazio
                            self.log_message("⚠ AVISO: Arquivo muito pequeno, pode estar corrompido")
                    
                    # Baixar arquivo do dispositivo
                    self.download_recording()
                else:
                    self.log_message("✗ ERRO: Arquivo não foi criado no dispositivo!")
                    self.log_message(f"Erro ao verificar: {check_result.stderr}")
                    messagebox.showerror("Erro", "Arquivo de gravação não foi criado no dispositivo!")
                
                # Tentar limpar arquivo do dispositivo (mesmo se download falhou)
                self.log_message("Limpando arquivo temporário do dispositivo...")
                cleanup_result = subprocess.run(
                    self.get_adb_command('-s', self.connected_device, 'shell', 'rm', self.device_file_path), 
                    capture_output=True, text=True
                )
                if cleanup_result.returncode == 0:
                    self.log_message("✓ Arquivo temporário removido do dispositivo")
                else:
                    self.log_message("⚠ Falha ao remover arquivo temporário")
            
            # Resetar interface
            self.is_recording = False
            self.record_button.config(text="🔴 Iniciar Gravação", style="Accent.TButton")
            self.time_label.config(text="Tempo: 00:00:00")
            
            self.log_message("=== Gravação finalizada ===")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao parar gravação: {str(e)}")
            self.log_message(f"ERRO ao parar gravação: {str(e)}")
            # Resetar interface mesmo com erro
            self.is_recording = False
            self.record_button.config(text="🔴 Iniciar Gravação", style="Accent.TButton")
            self.time_label.config(text="Tempo: 00:00:00")
    
    def download_recording(self):
        """Baixa o arquivo de gravação do dispositivo"""
        try:
            self.log_message("=== Iniciando download do arquivo ===")
            self.log_message(f"Origem: {self.device_file_path}")
            self.log_message(f"Destino: {self.current_file_path}")
            
            # Verificar se pasta de destino existe
            output_dir = os.path.dirname(self.current_file_path)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                self.log_message(f"Pasta criada: {output_dir}")
            
            # Comando de download
            cmd = self.get_adb_command('-s', self.connected_device, 'pull', self.device_file_path, self.current_file_path)
            cmd_str = ' '.join(cmd)
            self.log_message(f"Comando pull: {cmd_str}")
            
            # Executar download
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            self.log_message(f"Código de retorno: {result.returncode}")
            if result.stdout:
                self.log_message(f"Saída: {result.stdout.strip()}")
            if result.stderr:
                self.log_message(f"Erros: {result.stderr.strip()}")
            
            if result.returncode == 0:
                # Verificar se arquivo foi criado localmente
                if os.path.exists(self.current_file_path):
                    file_size = os.path.getsize(self.current_file_path)
                    file_size_mb = file_size / (1024 * 1024)
                    self.log_message(f"✓ Download concluído! Tamanho: {file_size_mb:.2f} MB")
                    
                    if file_size < 1024:  # Menos de 1KB
                        self.log_message("⚠ AVISO: Arquivo local muito pequeno!")
                        messagebox.showwarning("Arquivo Pequeno", 
                                             f"O arquivo baixado tem apenas {file_size} bytes. Pode estar corrompido.")
                    else:
                        # Sucesso! Perguntar se quer abrir pasta
                        if messagebox.askyesno("Download Concluído", 
                                             f"✓ Arquivo salvo com sucesso!\n\n"
                                             f"Local: {self.current_file_path}\n"
                                             f"Tamanho: {file_size_mb:.2f} MB\n\n"
                                             f"Deseja abrir a pasta?"):
                            try:
                                os.startfile(self.output_folder)
                            except:
                                # Fallback para outros sistemas
                                import webbrowser
                                webbrowser.open(f"file://{self.output_folder}")
                else:
                    self.log_message("✗ ERRO: Arquivo não foi criado localmente!")
                    messagebox.showerror("Erro de Download", 
                                       "O download foi reportado como sucesso, mas o arquivo não foi criado!")
            else:
                self.log_message(f"✗ ERRO no download: código {result.returncode}")
                messagebox.showerror("Erro de Download", 
                                   f"Falha no download:\n{result.stderr}")
                
        except subprocess.TimeoutExpired:
            self.log_message("✗ ERRO: Timeout no download (120s)")
            messagebox.showerror("Timeout", "Download demorou mais de 2 minutos e foi cancelado!")
        except Exception as e:
            self.log_message(f"✗ ERRO no download: {str(e)}")
            messagebox.showerror("Erro", f"Erro inesperado no download: {str(e)}")
    
    def update_timer(self):
        """Atualiza o timer de gravação"""
        if self.is_recording:
            elapsed = time.time() - self.start_time
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)
            
            time_str = f"Tempo: {hours:02d}:{minutes:02d}:{seconds:02d}"
            self.time_label.config(text=time_str)
            
            # Agendar próxima atualização
            self.root.after(1000, self.update_timer)
    
    def take_screenshot(self):
        """Captura screenshot do dispositivo"""
        if not self.connected_device:
            messagebox.showerror("Erro", "Nenhum dispositivo conectado!")
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            local_path = os.path.join(self.output_folder, filename)
            device_path = f"/sdcard/screenshot_{timestamp}.png"
            
            # Capturar screenshot
            subprocess.run(self.get_adb_command('-s', self.connected_device, 'shell', 'screencap', '-p', device_path), 
                          capture_output=True, timeout=10)
            
            # Baixar arquivo
            subprocess.run(self.get_adb_command('-s', self.connected_device, 'pull', device_path, local_path), 
                          capture_output=True, timeout=30)
            
            # Limpar arquivo do dispositivo
            subprocess.run(self.get_adb_command('-s', self.connected_device, 'shell', 'rm', device_path), 
                          capture_output=True)
            
            self.log_message(f"Screenshot salvo: {filename}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao capturar screenshot: {str(e)}")
            self.log_message(f"ERRO ao capturar screenshot: {str(e)}")
    
    def test_recording(self):
        """Executa um teste rápido de gravação de 10 segundos"""
        if not self.connected_device:
            messagebox.showerror("Erro", "Nenhum dispositivo conectado!")
            return
        
        if self.is_recording:
            messagebox.showwarning("Aviso", "Já há uma gravação em andamento!")
            return
        
        self.log_message("=== INICIANDO TESTE RÁPIDO ===")
        
        try:
            # Configurações do teste
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"TESTE_10s_{timestamp}.mp4"
            test_file_path = os.path.join(self.output_folder, filename)
            device_path = f"/sdcard/TESTE_10s_{timestamp}.mp4"
            
            # Comando simplificado para teste
            cmd = self.get_adb_command('-s', self.connected_device, 'shell', 'screenrecord', 
                                     '--time-limit', '10', '--bit-rate', '4M', device_path)
            
            cmd_str = ' '.join(cmd)
            self.log_message(f"Comando teste: {cmd_str}")
            self.log_message("Gravando por 10 segundos...")
            
            # Desabilitar botões durante teste
            self.test_button.config(state="disabled", text="⏳ Testando...")
            self.record_button.config(state="disabled")
            self.screenshot_button.config(state="disabled")
            
            # Executar gravação síncrona
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            
            # Log da execução
            self.log_message(f"Código de retorno: {result.returncode}")
            if result.stdout:
                self.log_message(f"Saída: {result.stdout.strip()}")
            if result.stderr:
                self.log_message(f"Erros: {result.stderr.strip()}")
            
            # Verificar resultado
            if result.returncode == 0:
                self.log_message("✓ Gravação de teste completada")
                
                # Verificar arquivo no dispositivo
                check_cmd = self.get_adb_command('-s', self.connected_device, 'shell', 'ls', '-la', device_path)
                check_result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=10)
                
                if check_result.returncode == 0:
                    file_info = check_result.stdout.strip()
                    self.log_message(f"Arquivo no dispositivo: {file_info}")
                    
                    # Baixar arquivo de teste
                    self.log_message("Baixando arquivo de teste...")
                    pull_cmd = self.get_adb_command('-s', self.connected_device, 'pull', device_path, test_file_path)
                    pull_result = subprocess.run(pull_cmd, capture_output=True, text=True, timeout=30)
                    
                    if pull_result.returncode == 0 and os.path.exists(test_file_path):
                        file_size = os.path.getsize(test_file_path)
                        file_size_mb = file_size / (1024 * 1024)
                        self.log_message(f"✓ TESTE CONCLUÍDO! Arquivo: {file_size_mb:.2f} MB")
                        messagebox.showinfo("Teste Concluído", 
                                          f"✓ Teste bem-sucedido!\n\n"
                                          f"Arquivo: {filename}\n"
                                          f"Tamanho: {file_size_mb:.2f} MB\n\n"
                                          f"A gravação normal deve funcionar!")
                    else:
                        self.log_message("✗ ERRO no download do teste")
                        messagebox.showerror("Erro no Teste", 
                                           f"Gravação funcionou, mas download falhou:\n{pull_result.stderr}")
                    
                    # Limpar arquivo de teste
                    subprocess.run(self.get_adb_command('-s', self.connected_device, 'shell', 'rm', device_path), 
                                 capture_output=True)
                else:
                    self.log_message("✗ ERRO: Arquivo de teste não foi criado")
                    messagebox.showerror("Teste Falhou", "Arquivo não foi criado no dispositivo!")
            else:
                self.log_message("✗ ERRO na gravação de teste")
                messagebox.showerror("Teste Falhou", f"Erro na gravação:\n{result.stderr}")
            
        except Exception as e:
            self.log_message(f"✗ ERRO no teste: {str(e)}")
            messagebox.showerror("Erro no Teste", f"Erro inesperado: {str(e)}")
        
        finally:
            # Reabilitar botões
            self.test_button.config(state="normal", text="🧪 Teste (10s)")
            self.record_button.config(state="normal")
            self.screenshot_button.config(state="normal")
            self.log_message("=== TESTE FINALIZADO ===")
    
    def load_settings(self):
        """Carrega configurações salvas"""
        try:
            # Usar diretório do usuário para configurações (funciona em executável)
            if getattr(sys, 'frozen', False):
                # Executável - usar pasta do usuário
                config_dir = os.path.expanduser("~/.GravadorTelaAndroid")
                os.makedirs(config_dir, exist_ok=True)
                settings_file = os.path.join(config_dir, "settings.json")
            else:
                # Script - usar pasta local
                settings_file = os.path.join(os.path.dirname(__file__), "settings.json")
            
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    self.output_folder = settings.get('output_folder', self.output_folder)
                    # Carregar outras configurações após a criação da interface
                    if hasattr(self, 'resolution_var'):
                        self.resolution_var.set(settings.get('resolution', '1920x1080'))
                        self.bitrate_var.set(settings.get('bitrate', '8'))
                        self.fps_var.set(settings.get('fps', '30'))
                        self.max_time_var.set(settings.get('max_time', '3'))
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
    
    def save_settings(self):
        """Salva configurações"""
        try:
            # Usar diretório do usuário para configurações (funciona em executável)
            if getattr(sys, 'frozen', False):
                # Executável - usar pasta do usuário
                config_dir = os.path.expanduser("~/.GravadorTelaAndroid")
                os.makedirs(config_dir, exist_ok=True)
                settings_file = os.path.join(config_dir, "settings.json")
            else:
                # Script - usar pasta local
                settings_file = os.path.join(os.path.dirname(__file__), "settings.json")
            
            settings = {
                'output_folder': self.output_folder,
                'resolution': self.resolution_var.get(),
                'bitrate': self.bitrate_var.get(),
                'fps': self.fps_var.get(),
                'max_time': self.max_time_var.get()
            }
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
    
    def on_closing(self):
        """Callback ao fechar aplicação"""
        if self.is_recording:
            if messagebox.askyesno("Gravação Ativa", "Há uma gravação em andamento. Deseja parar e fechar?"):
                self.stop_recording()
                self.save_settings()
                self.root.destroy()
        else:
            self.save_settings()
            self.root.destroy()

def main():
    root = tk.Tk()
    
    # Criar aplicação
    app = AndroidScreenRecorder(root)
    
    # Configurar evento de fechamento
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Centralizar janela
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    # Iniciar loop principal
    root.mainloop()

if __name__ == "__main__":
    main() 