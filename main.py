import sys
import os
import time
import json
import subprocess
import threading
from datetime import datetime
from pathlib import Path
from PIL import Image

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QSpinBox, QLineEdit,
    QFileDialog, QTabWidget, QFrame, QTextEdit, QMessageBox,
    QGroupBox
)
from PySide6.QtCore import Qt, QTimer, Signal, Slot, QSize
from PySide6.QtGui import QIcon, QPixmap, QFont, QColor, QPalette

# Informações da aplicação
APP_NAME = "Screnoid"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Deyvison Chaves"

# Paleta de cores do tema escuro
COLORS = {
    'bg_dark': '#1E1E1E',
    'bg_medium': '#252526',
    'bg_light': '#2D2D30',
    'accent_blue': 'rgb(53, 51, 51)',  # Alterado para o novo tom
    'accent_blue_hover': 'rgb(73, 71, 71)',  # Um pouco mais claro para hover
    'accent_red': 'rgb(5, 65, 67)',  # Novo tom para botões laranja
    'accent_red_hover': 'rgb(15, 95, 97)',  # Um pouco mais claro para hover
    'text_primary': '#FFFFFF',
    'text_secondary': '#CCCCCC',
    'border': '#3F3F3F',
    'success': '#4EC9B0',
    'warning': '#CE9178',
    'error': '#F44747',
    'info': '#569CD6'
}

class DarkPalette(QPalette):
    def __init__(self):
        super().__init__()
        self.setColor(QPalette.Window, QColor(COLORS['bg_dark']))
        self.setColor(QPalette.WindowText, QColor(COLORS['text_primary']))
        self.setColor(QPalette.Base, QColor(COLORS['bg_medium']))
        self.setColor(QPalette.AlternateBase, QColor(COLORS['bg_light']))
        self.setColor(QPalette.ToolTipBase, QColor(COLORS['text_primary']))
        self.setColor(QPalette.ToolTipText, QColor(COLORS['text_primary']))
        self.setColor(QPalette.Text, QColor(COLORS['text_primary']))
        self.setColor(QPalette.Button, QColor(COLORS['bg_medium']))
        self.setColor(QPalette.ButtonText, QColor(COLORS['text_primary']))
        self.setColor(QPalette.BrightText, QColor(COLORS['text_primary']))
        self.setColor(QPalette.Highlight, QColor(COLORS['accent_blue']))
        self.setColor(QPalette.HighlightedText, QColor(COLORS['text_primary']))
        self.setColor(QPalette.Disabled, QPalette.Text, QColor(COLORS['text_secondary']))
        self.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(COLORS['text_secondary']))

class LogWidget(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['bg_medium']};
                color: {COLORS['text_primary']};
                font-family: 'Consolas';
                font-size: 9pt;
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 8px;
            }}
        """)
    
    def log_message(self, message, msg_type="info"):
        color_map = {
            "info": COLORS['info'],
            "success": COLORS['success'],
            "warning": COLORS['warning'],
            "error": COLORS['error']
        }
        color = color_map.get(msg_type, COLORS['text_primary'])
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f'<span style="color: {color}">[{timestamp}] {message}</span><br>'
        self.append(formatted_msg)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

class AndroidScreenRecorder(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(950, 750)
        
        # Aplicar tema escuro
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS['bg_dark']};
            }}
            QWidget {{
                background-color: {COLORS['bg_dark']};
                color: {COLORS['text_primary']};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 8px;
                background-color: {COLORS['bg_medium']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
                background-color: {COLORS['bg_medium']};
            }}
            QPushButton {{
                background-color: {COLORS['accent_blue']};
                color: {COLORS['text_primary']};
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-weight: bold;
                min-width: 150px;
                min-height: 35px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent_blue_hover']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['accent_blue']};
            }}
            QPushButton:disabled {{
                background-color: {COLORS['bg_light']};
                color: {COLORS['text_secondary']};
            }}
            QPushButton[class="icon-button"] {{
                min-width: 40px;
                min-height: 35px;
                padding: 8px;
            }}
            QComboBox, QSpinBox, QLineEdit {{
                background-color: {COLORS['bg_light']};
                color: {COLORS['text_primary']};
                padding: 4px 8px;
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
            }}
            QComboBox:drop-down {{
                border: none;
                padding-right: 8px;
            }}
            QComboBox:down-arrow {{
                image: none;
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                border: none;
                background-color: {COLORS['bg_light']};
                padding: 2px;
            }}
            QTabWidget::pane {{
                border: 1px solid {COLORS['border']};
                background-color: {COLORS['bg_medium']};
                border-radius: 4px;
            }}
            QTabBar::tab {{
                background-color: {COLORS['bg_medium']};
                color: {COLORS['text_primary']};
                padding: 8px 16px;
                border: 1px solid {COLORS['border']};
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background-color: {COLORS['accent_blue']};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {COLORS['bg_light']};
            }}
            QLabel {{
                color: {COLORS['text_primary']};
            }}
        """)

        # Configurar ícone da janela
        if os.path.exists("screnoid.ico"):
            self.setWindowIcon(QIcon("screnoid.ico"))
        
        # Variáveis de controle
        self.is_recording = False
        self.is_mirroring = False
        self.connected_device = None
        self.recording_process = None
        self.mirroring_process = None
        # Definir pasta padrão Screnoid em Documentos
        self.output_folder = os.path.join(os.path.expanduser('~'), 'Documents', 'Screnoid')
        # Criar pasta de saída se não existir
        os.makedirs(self.output_folder, exist_ok=True)
        
        # Configurar caminho do ADB local
        self.setup_adb_path()
        
        # Carregar configurações
        self.load_settings()
        
        # Criar interface
        self.setup_ui()
        
        # Timer para atualização do tempo de gravação
        self.recording_timer = QTimer()
        self.recording_timer.timeout.connect(self.update_timer)
        self.recording_start_time = 0
        
        # Verificar ADB na inicialização
        self.check_adb_connection()
    
    def setup_adb_path(self):
        """Configura o caminho para o ADB local"""
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        platform_tools_dir = os.path.join(base_dir, "platform-tools")
        
        if os.name == 'nt':
            self.adb_path = os.path.join(platform_tools_dir, "adb.exe")
        else:
            self.adb_path = os.path.join(platform_tools_dir, "adb")
        
        if not os.path.exists(self.adb_path):
            self.adb_path = "adb"
            self.using_local_adb = False
        else:
            self.using_local_adb = True
    
    def setup_ui(self):
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header_layout = QVBoxLayout()
        img_label = QLabel()
        img_label.setAlignment(Qt.AlignCenter)
        img_label.setPixmap(QPixmap('Screnoid_Nome.png').scaledToHeight(60, Qt.SmoothTransformation))
        header_layout.addWidget(img_label)
        main_layout.addLayout(header_layout)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet(f"background-color: {COLORS['border']};")
        main_layout.addWidget(separator)
        
        # Seção de Conexão
        connection_group = QGroupBox("🔗 Conexão com Dispositivo")
        connection_layout = QVBoxLayout(connection_group)
        connection_layout.setSpacing(10)
        
        # Status e botão atualizar
        status_layout = QHBoxLayout()
        status_label = QLabel("Status:")
        self.status_text = QLabel("🔍 Verificando...")
        self.status_text.setStyleSheet(f"color: {COLORS['warning']};")
        refresh_button = QPushButton("🔃 Atualizar")
        refresh_button.clicked.connect(self.refresh_devices)
        
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.status_text, stretch=1)
        status_layout.addWidget(refresh_button)
        connection_layout.addLayout(status_layout)
        
        # Dispositivo
        device_layout = QHBoxLayout()
        device_label = QLabel("Dispositivo:")
        self.device_combo = QComboBox()
        self.device_combo.currentIndexChanged.connect(self.on_device_selected)
        adb_status = "📱 Local" if self.using_local_adb else "💻 Sistema"
        self.adb_status_label = QLabel(adb_status)
        
        device_layout.addWidget(device_label)
        device_layout.addWidget(self.device_combo, stretch=1)
        device_layout.addWidget(self.adb_status_label)
        connection_layout.addLayout(device_layout)
        
        main_layout.addWidget(connection_group)
        
        # Abas
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {COLORS['border']};
                background-color: {COLORS['bg_medium']};
                border-radius: 4px;
            }}
        """)
        self.tab_widget.addTab(self.create_recording_tab(), "📹 Gravação")
        self.tab_widget.addTab(self.create_mirroring_tab(), "🖥️ Segunda Tela")
        self.tab_widget.addTab(self.create_about_tab(), "ℹ️ Sobre")
        main_layout.addWidget(self.tab_widget)

    def create_recording_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)
        
        # Configurações
        settings_group = QGroupBox("⚙️ Configurações de Gravação")
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.setSpacing(10)
        
        # Linha única: Resolução, Bitrate, FPS, Tempo Máx
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(18)

        resolution_label = QLabel("Resolução:")
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["1920x1080", "1280x720", "854x480", "640x360", "Auto"])

        bitrate_label = QLabel("Bitrate:")
        self.bitrate_spin = QSpinBox()
        self.bitrate_spin.setRange(1, 20)
        self.bitrate_spin.setValue(8)
        self.bitrate_spin.setSuffix(" Mbps")

        fps_label = QLabel("FPS:")
        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["15", "24", "30", "60"])
        self.fps_combo.setCurrentText("30")

        time_label = QLabel("Tempo Máx (min):")
        self.max_time_spin = QSpinBox()
        self.max_time_spin.setRange(1, 180)
        self.max_time_spin.setValue(3)

        row1_layout.addWidget(resolution_label)
        row1_layout.addWidget(self.resolution_combo)
        row1_layout.addSpacing(12)
        row1_layout.addWidget(bitrate_label)
        row1_layout.addWidget(self.bitrate_spin)
        row1_layout.addSpacing(12)
        row1_layout.addWidget(fps_label)
        row1_layout.addWidget(self.fps_combo)
        row1_layout.addSpacing(12)
        row1_layout.addWidget(time_label)
        row1_layout.addWidget(self.max_time_spin)
        row1_layout.addStretch(1)
        settings_layout.addLayout(row1_layout)

        # Linha 2: Pasta de Saída
        row2_layout = QHBoxLayout()
        output_label = QLabel("Pasta Saída:")
        self.output_path = QLineEdit(self.output_folder)
        browse_button = QPushButton("📂")
        browse_button.setFixedWidth(40)
        browse_button.setProperty("class", "icon-button")  # Adiciona uma classe especial
        browse_button.clicked.connect(self.choose_output_folder)

        row2_layout.addWidget(output_label)
        row2_layout.addWidget(self.output_path, stretch=1)
        row2_layout.addWidget(browse_button)
        settings_layout.addLayout(row2_layout)
        
        layout.addWidget(settings_group)
        
        # Controles
        control_group = QGroupBox("🎮 Controles")
        control_layout = QVBoxLayout(control_group)
        control_layout.setSpacing(18)
        control_layout.setContentsMargins(18, 18, 18, 18)

        # Layout dos botões em grid
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(18)

        button_width = 220
        button_height = 48
        button_style = f"font-size: 16px; min-width: {button_width}px; min-height: {button_height}px; font-weight: bold;"

        self.record_button = QPushButton("⏺️ Iniciar Gravação")
        self.record_button.setMinimumSize(button_width, button_height)
        self.record_button.setMaximumHeight(button_height)
        self.record_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent_red']};
                {button_style}
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent_red_hover']};
            }}
        """)
        self.record_button.clicked.connect(self.toggle_recording)

        self.screenshot_button = QPushButton("🖼️ Screenshot")
        self.screenshot_button.setMinimumSize(button_width, button_height)
        self.screenshot_button.setMaximumHeight(button_height)
        self.screenshot_button.setStyleSheet(f"background-color: {COLORS['accent_blue']}; {button_style}")
        self.screenshot_button.clicked.connect(self.take_screenshot)

        self.test_button = QPushButton("🧪 Teste (10s)")
        self.test_button.setMinimumSize(button_width, button_height)
        self.test_button.setMaximumHeight(button_height)
        self.test_button.setStyleSheet(f"background-color: {COLORS['accent_blue']}; {button_style}")
        self.test_button.clicked.connect(self.test_recording)

        # Adicionar botões ao layout
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.record_button)
        buttons_layout.addWidget(self.screenshot_button)
        buttons_layout.addWidget(self.test_button)
        buttons_layout.addStretch(1)
        control_layout.addLayout(buttons_layout)

        # Timer
        self.time_label = QLabel("⏱️ Tempo: 00:00:00")
        self.time_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        self.time_label.setAlignment(Qt.AlignCenter)
        control_layout.addWidget(self.time_label)
        
        layout.addWidget(control_group)
        
        # Log
        log_group = QGroupBox("📋 Log")
        log_layout = QVBoxLayout(log_group)
        self.log_widget = LogWidget()
        log_layout.addWidget(self.log_widget)
        layout.addWidget(log_group)
        
        return tab

    def create_mirroring_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)

        # Configurações em linha única
        settings_group = QGroupBox("⚙️ Configurações")
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.setSpacing(18)

        # Primeira linha: Resolução e FPS
        row1_layout = QHBoxLayout()
        resolution_label = QLabel("Resolução:")
        self.mirror_resolution_combo = QComboBox()
        self.mirror_resolution_combo.addItems(["1920x1080", "1280x720", "854x480", "640x360"])

        fps_label = QLabel("FPS:")
        self.mirror_fps_combo = QComboBox()
        self.mirror_fps_combo.addItems(["60", "30", "24", "15"])

        row1_layout.addWidget(resolution_label)
        row1_layout.addWidget(self.mirror_resolution_combo)
        row1_layout.addSpacing(12)
        row1_layout.addWidget(fps_label)
        row1_layout.addWidget(self.mirror_fps_combo)
        row1_layout.addStretch(1)
        settings_layout.addLayout(row1_layout)

        # Segunda linha: Modo de operação
        row2_layout = QHBoxLayout()
        mode_label = QLabel("Modo:")
        self.mirror_mode_combo = QComboBox()
        self.mirror_mode_combo.addItems([
            "📱 Android → PC (Espelhar Android)",
            "🖥️ PC → Android (Espelhar PC)",
            "📺 Estender Monitor"
        ])
        self.mirror_mode_combo.currentIndexChanged.connect(self.on_mirror_mode_changed)

        row2_layout.addWidget(mode_label)
        row2_layout.addWidget(self.mirror_mode_combo, stretch=1)
        settings_layout.addLayout(row2_layout)

        layout.addWidget(settings_group)
        
        # Controles
        control_group = QGroupBox("🎮 Controles")
        control_layout = QVBoxLayout(control_group)
        control_layout.setSpacing(10)
        
        self.mirror_button = QPushButton("🖥️ Iniciar Segunda Tela")
        self.mirror_button.clicked.connect(self.toggle_mirroring)
        self.mirror_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent_red']};
                min-width: 150px;
                min-height: 35px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent_red_hover']};
            }}
        """)
        control_layout.addWidget(self.mirror_button)
        
        layout.addWidget(control_group)
        
        # Status e instruções
        self.mirror_status_label = QLabel()
        self.mirror_status_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        self.mirror_status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.mirror_status_label)

        # Log específico para Segunda Tela
        log_group = QGroupBox("📋 Log")
        log_layout = QVBoxLayout(log_group)
        self.mirror_log = LogWidget()
        log_layout.addWidget(self.mirror_log)
        layout.addWidget(log_group)
        
        layout.addStretch()
        return tab

    def create_about_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(18)

        title = QLabel(f"<span style='font-size:22px; font-weight:bold; color:{COLORS['accent_blue']}'>Screnoid</span>")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        desc = QLabel("""
            <div style='font-size:15px; color:{color};'>
            Aplicação para Gravação de Tela e Simulação de Segundo Monitor para Computadores e Notebook em Dispositivos Android.<br><br>
            <b>Versão:</b> {version}<br>
            <b>Desenvolvido por:</b> LabCoder<br>
            <b>Ano:</b> 2025<br>
            <b>Autor:</b> Deyvison Chaves<br>
            <b>Contato:</b> <a href='mailto:dev.deyvison@gmail.com' style='color:{accent};'>dev.deyvison@gmail.com</a>
            </div>
        """.format(
            color=COLORS['text_primary'],
            accent=COLORS['accent_blue'],
            version=APP_VERSION
        ))
        desc.setOpenExternalLinks(True)
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)

        layout.addStretch(1)
        return tab

    def on_mirror_mode_changed(self, index):
        # Atualiza o texto do botão e instruções baseado no modo
        mode_texts = [
            "🖥️ Iniciar Espelhamento",
            "📱 Iniciar Espelhamento Reverso",
            "📺 Iniciar Modo Extensão"
        ]
        self.mirror_button.setText(mode_texts[index])

    def toggle_mirroring(self):
        if not self.is_mirroring:
            self.start_mirroring()
        else:
            self.stop_mirroring()

    def setup_virtual_display(self):
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            usbmmidd_dir = os.path.join(base_dir, "usbmmidd_v2")
            
            # Instalar/Atualizar driver
            subprocess.run([
                os.path.join(usbmmidd_dir, "deviceinstaller64.exe"),
                "install",
                os.path.join(usbmmidd_dir, "usbmmidd.inf"),
                "USB\\Vid_0547&Pid_1002"
            ], check=True)
            
            # Criar monitor virtual
            subprocess.run([
                os.path.join(usbmmidd_dir, "deviceinstaller64.exe"),
                "enableidd", "1"
            ], check=True)

            self.mirror_log.log_message("Monitor virtual criado com sucesso!", "success")
            return True
        except Exception as e:
            self.mirror_log.log_message(f"Erro ao criar monitor virtual: {e}", "error")
            return False

    def remove_virtual_display(self):
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            usbmmidd_dir = os.path.join(base_dir, "usbmmidd_v2")
            
            # Remover monitor virtual
            subprocess.run([
                os.path.join(usbmmidd_dir, "deviceinstaller64.exe"),
                "enableidd", "0"
            ], check=True)

            self.mirror_log.log_message("Monitor virtual removido com sucesso!", "success")
        except Exception as e:
            self.mirror_log.log_message(f"Erro ao remover monitor virtual: {e}", "error")

    def start_mirroring(self):
        if not self.connected_device:
            QMessageBox.warning(self, "Erro", "Nenhum dispositivo conectado!")
            return

        # Verificar se o ADB está funcionando
        try:
            adb_version = subprocess.run(
                [self.adb_path, "version"],
                capture_output=True,
                text=True,
                check=True
            )
            self.mirror_log.log_message(f"ADB versão: {adb_version.stdout.strip()}", "info")
            
            # Verificar status do dispositivo
            adb_devices = subprocess.run(
                [self.adb_path, "devices"], 
                capture_output=True,
                text=True,
                check=True
            )
            self.mirror_log.log_message(f"Dispositivos ADB: {adb_devices.stdout.strip()}", "info")
            
            if self.connected_device not in adb_devices.stdout:
                raise Exception("Dispositivo não encontrado ou não autorizado")
            
            # Verificar se o dispositivo está respondendo
            state = subprocess.run(
                [self.adb_path, "-s", self.connected_device, "get-state"],
                capture_output=True,
                text=True,
                check=True
            )
            self.mirror_log.log_message(f"Estado do dispositivo: {state.stdout.strip()}", "info")
            
        except Exception as e:
            self.mirror_log.log_message(f"Erro ao verificar ADB: {str(e)}", "error")
            QMessageBox.critical(self, "Erro", "Falha ao inicializar ADB. Verifique se o dispositivo está conectado e autorizado.")
            return

        # Verificar pasta do scrcpy
        base_dir = os.path.dirname(os.path.abspath(__file__))
        scrcpy_dir = os.path.join(base_dir, "scrcpy")
        scrcpy_exe = os.path.join(scrcpy_dir, "scrcpy.exe") if os.name == "nt" else os.path.join(scrcpy_dir, "scrcpy")
        scrcpy_server = os.path.join(scrcpy_dir, "scrcpy-server")
        
        # Verificar arquivos necessários
        if not os.path.exists(scrcpy_exe):
            QMessageBox.critical(self, "Erro", "scrcpy.exe não encontrado na pasta local")
            return
            
        if not os.path.exists(scrcpy_server):
            QMessageBox.critical(self, "Erro", "scrcpy-server não encontrado na pasta local")
            return

        try:
            # Primeiro, vamos tentar enviar o servidor para o dispositivo
            self.mirror_log.log_message("Enviando servidor scrcpy para o dispositivo...", "info")
            push_result = subprocess.run(
                [self.adb_path, "-s", self.connected_device, "push", scrcpy_server, "/data/local/tmp/scrcpy-server"],
                capture_output=True,
                text=True
            )
            if push_result.returncode != 0:
                raise Exception(f"Erro ao enviar servidor: {push_result.stderr}")
            
            # Dar permissão de execução ao servidor
            subprocess.run(
                [self.adb_path, "-s", self.connected_device, "shell", "chmod 777 /data/local/tmp/scrcpy-server"],
                check=True
            )

            # Configuração básica do scrcpy
            cmd = [
                scrcpy_exe,
                "-s", self.connected_device,
                "--no-audio",
                "-v"
            ]
            
            self.mirror_log.log_message(f"Executando comando: {' '.join(cmd)}", "info")
            
            # Iniciar processo com captura de saída
            self.mirroring_process = subprocess.Popen(
                cmd,
                cwd=scrcpy_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Criar threads para monitorar a saída em tempo real
            def monitor_output(pipe, log_type):
                try:
                    for line in pipe:
                        line = line.strip()
                        if line:  # Só registrar linhas não vazias
                            self.mirror_log.log_message(line, log_type)
                            
                            # Verificar por mensagens específicas de erro
                            if "ERROR:" in line:
                                self.mirror_log.log_message(f"Erro detectado: {line}", "error")
                                self.stop_mirroring()
                except Exception as e:
                    self.mirror_log.log_message(f"Erro ao monitorar saída: {str(e)}", "error")

            # Iniciar threads de monitoramento
            stdout_thread = threading.Thread(target=monitor_output, args=(self.mirroring_process.stdout, "info"), daemon=True)
            stderr_thread = threading.Thread(target=monitor_output, args=(self.mirroring_process.stderr, "error"), daemon=True)
            
            stdout_thread.start()
            stderr_thread.start()

            self.is_mirroring = True
            self.mirror_button.setText("⏹️ Parar")
            self.mirror_button.setStyleSheet("""
                QPushButton {
                    background-color: #C73E1D;
                }
                QPushButton:hover {
                    background-color: #A93315;
                }
            """)
            
            # Aguardar um pouco para ver se o processo inicia corretamente
            time.sleep(2)
            
            if self.mirroring_process.poll() is not None:
                # Coletar toda a saída disponível
                stdout, stderr = self.mirroring_process.communicate()
                exit_code = self.mirroring_process.poll()
                
                error_msg = stderr.strip() if stderr else stdout.strip()
                if not error_msg:
                    error_msg = "Nenhuma mensagem de erro disponível"
                
                if exit_code != 0:
                    raise Exception(f"Processo terminou com código {exit_code}. Erro: {error_msg}")
                else:
                    self.mirror_log.log_message("Processo encerrado normalmente", "info")
            else:
                self.mirror_log.log_message("scrcpy iniciado com sucesso!", "success")
                
        except FileNotFoundError:
            QMessageBox.critical(self, "scrcpy não encontrado", "O programa scrcpy não está instalado nem na pasta local nem no PATH do sistema.\n\nBaixe em: https://github.com/Genymobile/scrcpy")
            self.mirror_log.log_message("scrcpy não encontrado no sistema.", "error")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao iniciar scrcpy: {e}")
            self.mirror_log.log_message(f"Erro ao iniciar scrcpy: {e}", "error")
            self.stop_mirroring()  # Limpar estado em caso de erro

    def stop_mirroring(self):
        self.is_mirroring = False
        self.mirror_button.setText("🖥️ Iniciar Segunda Tela")
        self.mirror_button.setStyleSheet("")

        # Parar scrcpy
        if self.mirroring_process:
            try:
                self.mirroring_process.terminate()
                self.mirror_log.log_message("scrcpy encerrado.", "info")
            except Exception as e:
                self.mirror_log.log_message(f"Erro ao encerrar scrcpy: {e}", "error")
            self.mirroring_process = None

        # Se estiver no modo extensão, remover monitor virtual
        if self.mirror_mode_combo.currentIndex() == 2:
            self.remove_virtual_display()
    
    def mirroring_loop(self, resolution, fps):
        try:
            # Implementar lógica de espelhamento aqui
            pass
        except Exception as e:
            self.log_widget.log_message(f"Erro no espelhamento: {str(e)}", "error")
            self.is_mirroring = False
    
    def check_adb_connection(self):
        try:
            result = subprocess.run([self.adb_path, "version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.log_widget.log_message("ADB conectado com sucesso!", "success")
                self.refresh_devices()
            else:
                self.log_widget.log_message("Erro ao conectar ao ADB", "error")
        except Exception as e:
            self.log_widget.log_message(f"Erro ao verificar ADB: {str(e)}", "error")
    
    def refresh_devices(self):
        try:
            result = subprocess.run([self.adb_path, "devices"], 
                                  capture_output=True, text=True)
            
            devices = []
            for line in result.stdout.split('\n')[1:]:
                if '\t' in line:
                    device = line.split('\t')[0]
                    devices.append(device)
            
            self.device_combo.clear()
            if devices:
                self.device_combo.addItems(devices)
                self.status_text.setText("✅ Dispositivo(s) encontrado(s)")
                self.status_text.setStyleSheet("color: #059862;")
            else:
                self.status_text.setText("❌ Nenhum dispositivo")
                self.status_text.setStyleSheet("color: #C73E1D;")
            
        except Exception as e:
            self.log_widget.log_message(f"Erro ao atualizar dispositivos: {str(e)}", "error")

    def on_device_selected(self, index):
        if index >= 0:
            self.connected_device = self.device_combo.currentText()
        else:
            self.connected_device = None
    
    def choose_output_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Selecionar Pasta de Saída",
            self.output_folder,
            QFileDialog.ShowDirsOnly
        )
        if folder:
            self.output_folder = folder
            self.output_path.setText(folder)
            self.save_settings()
    
    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        if not self.connected_device:
            QMessageBox.warning(self, "Erro", "Nenhum dispositivo conectado!")
            return
        
        try:
            # Configurar parâmetros
            resolution = self.resolution_combo.currentText()
            bitrate = int(self.bitrate_spin.value()) * 1000000  # Converter para bits
            fps = self.fps_combo.currentText()
            max_time = int(self.max_time_spin.value()) * 60  # Converter para segundos
            
            # Preparar comando
            cmd = [self.adb_path, "-s", self.connected_device, "shell"]
            record_cmd = ["screenrecord"]
            
            if resolution != "Auto":
                record_cmd.extend(["--size", resolution])
            
            record_cmd.extend([
                "--bit-rate", str(bitrate),
                "--time-limit", str(max_time),
                "--verbose",
                "/sdcard/screen.mp4"
            ])
            
            # Iniciar gravação
            self.recording_process = subprocess.Popen(
                cmd + record_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Atualizar interface
            self.is_recording = True
            self.record_button.setText("⏹️ Parar Gravação")
            self.record_button.setStyleSheet("""
                QPushButton {
                    background-color: #C73E1D;
                }
                QPushButton:hover {
                    background-color: #A93315;
                }
            """)
            
            # Iniciar timer
            self.recording_start_time = time.time()
            self.recording_timer.start(1000)  # Atualizar a cada segundo
            
            self.log_widget.log_message("Gravação iniciada!", "success")
            
        except Exception as e:
            self.log_widget.log_message(f"Erro ao iniciar gravação: {str(e)}", "error")
            self.is_recording = False
    
    def stop_recording(self):
        if not self.is_recording:
            return
        
        try:
            # Parar gravação
            if self.recording_process:
                self.recording_process.terminate()
            
            # Enviar Ctrl+C para o processo adb
            subprocess.run([self.adb_path, "-s", self.connected_device, "shell", "killall", "screenrecord"])
            
            # Aguardar um pouco
            time.sleep(1)
            
            # Download do arquivo
            self.download_recording()
            
            # Limpar
            self.recording_process = None
            self.is_recording = False
            self.recording_timer.stop()
            
            # Atualizar interface
            self.record_button.setText("⏺️ Iniciar Gravação")
            self.record_button.setStyleSheet("")
            
            self.log_widget.log_message("Gravação finalizada!", "success")
            
        except Exception as e:
            self.log_widget.log_message(f"Erro ao parar gravação: {str(e)}", "error")
    
    def download_recording(self):
        try:
            # Criar nome do arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"gravacao_{timestamp}.mp4"
            output_path = os.path.join(self.output_folder, filename)
            
            # Download do arquivo
            subprocess.run([
                self.adb_path, "-s", self.connected_device,
                "pull", "/sdcard/screen.mp4", output_path
            ])
            
            # Remover arquivo do dispositivo
            subprocess.run([
                self.adb_path, "-s", self.connected_device,
                "shell", "rm", "/sdcard/screen.mp4"
            ])
            
            self.log_widget.log_message(f"Arquivo salvo em: {output_path}", "success")
            
        except Exception as e:
            self.log_widget.log_message(f"Erro ao baixar gravação: {str(e)}", "error")
    
    def update_timer(self):
        if self.is_recording:
            elapsed = int(time.time() - self.recording_start_time)
            hours = elapsed // 3600
            minutes = (elapsed % 3600) // 60
            seconds = elapsed % 60
            self.time_label.setText(f"⏱️ Tempo: {hours:02d}:{minutes:02d}:{seconds:02d}")
    
    def take_screenshot(self):
        if not self.connected_device:
            QMessageBox.warning(self, "Erro", "Nenhum dispositivo conectado!")
            return
        
        try:
            # Criar nome do arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            output_path = os.path.join(self.output_folder, filename)
            
            # Capturar screenshot
            subprocess.run([
                self.adb_path, "-s", self.connected_device,
                "shell", "screencap", "-p", "/sdcard/screen.png"
            ])
            
            # Download do arquivo
            subprocess.run([
                self.adb_path, "-s", self.connected_device,
                "pull", "/sdcard/screen.png", output_path
            ])
            
            # Remover arquivo do dispositivo
            subprocess.run([
                self.adb_path, "-s", self.connected_device,
                "shell", "rm", "/sdcard/screen.png"
            ])
            
            self.log_widget.log_message(f"Screenshot salvo em: {output_path}", "success")
            
        except Exception as e:
            self.log_widget.log_message(f"Erro ao capturar screenshot: {str(e)}", "error")
    
    def test_recording(self):
        if not self.connected_device:
            QMessageBox.warning(self, "Erro", "Nenhum dispositivo conectado!")
            return
        
        try:
            # Salvar valores atuais
            old_time = self.max_time_spin.value()
            
            # Configurar para teste de 10 segundos
            self.max_time_spin.setValue(1)
            
            # Iniciar gravação
            self.start_recording()
            
            # Restaurar valores
            self.max_time_spin.setValue(old_time)
            
            self.log_widget.log_message("Teste de gravação iniciado (10 segundos)...", "info")
            
        except Exception as e:
            self.log_widget.log_message(f"Erro no teste: {str(e)}", "error")
    
    def load_settings(self):
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r") as f:
                    settings = json.load(f)
                    # Só aceita a pasta se não for MiniPcCapture
                    output_folder = settings.get("output_folder", self.output_folder)
                    if 'MiniPcCapture' not in output_folder:
                        self.output_folder = output_folder
                    # Criar pasta se não existir
                    os.makedirs(self.output_folder, exist_ok=True)
        except Exception as e:
            self.log_widget.log_message(f"Erro ao carregar configurações: {str(e)}", "error")
    
    def save_settings(self):
        try:
            settings = {
                "output_folder": self.output_folder
            }
            
            with open("settings.json", "w") as f:
                json.dump(settings, f, indent=4)
                
        except Exception as e:
            self.log_widget.log_message(f"Erro ao salvar configurações: {str(e)}", "error")
    
    def closeEvent(self, event):
        # Parar processos em execução
        if self.is_recording:
            self.stop_recording()
        if self.is_mirroring:
            self.stop_mirroring()
        
        # Salvar configurações
        self.save_settings()
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    # Aplicar tema escuro global
    app.setStyle("Fusion")
    app.setPalette(DarkPalette())
    
    window = AndroidScreenRecorder()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 