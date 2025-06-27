"""
Utilitários para comandos ADB e manipulação de dispositivos Android
"""

import subprocess
import json
import re
import os
from typing import List, Dict, Optional, Tuple

class ADBUtils:
    """Classe com utilitários para comandos ADB"""
    
    def __init__(self):
        """Inicializa configurando o caminho do ADB"""
        self.setup_adb_path()
    
    def setup_adb_path(self):
        """Configura o caminho para o ADB local"""
        # Determinar o diretório do script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Caminho para platform-tools
        platform_tools_dir = os.path.join(script_dir, "platform-tools")
        
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
    
    def check_adb_available(self) -> bool:
        """Verifica se ADB está disponível no sistema"""
        try:
            result = subprocess.run(self.get_adb_command('version'), capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def get_connected_devices(self) -> List[Dict[str, str]]:
        """Retorna lista de dispositivos conectados com informações detalhadas"""
        devices = []
        try:
            result = subprocess.run(self.get_adb_command('devices', '-l'), capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Pular primeira linha
                for line in lines:
                    if line.strip() and '\tdevice' in line:
                        parts = line.split()
                        device_id = parts[0]
                        
                        # Obter informações adicionais
                        device_info = {
                            'id': device_id,
                            'status': 'device',
                            'model': self.get_device_property(device_id, 'ro.product.model'),
                            'brand': self.get_device_property(device_id, 'ro.product.brand'),
                            'version': self.get_device_property(device_id, 'ro.build.version.release'),
                            'sdk': self.get_device_property(device_id, 'ro.build.version.sdk'),
                            'resolution': self.get_screen_resolution(device_id)
                        }
                        devices.append(device_info)
        except Exception as e:
            print(f"Erro ao obter dispositivos: {e}")
        
        return devices
    
    def get_device_property(self, device_id: str, property_name: str) -> str:
        """Obtém propriedade específica do dispositivo"""
        try:
            result = subprocess.run(
                self.get_adb_command('-s', device_id, 'shell', 'getprop', property_name),
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return "Desconhecido"
    
    def get_screen_resolution(self, device_id: str) -> str:
        """Obtém resolução da tela do dispositivo"""
        try:
            result = subprocess.run(
                self.get_adb_command('-s', device_id, 'shell', 'wm', 'size'),
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                # Formato: "Physical size: 1920x1080"
                match = re.search(r'(\d+x\d+)', result.stdout)
                if match:
                    return match.group(1)
        except Exception:
            pass
        return "Desconhecida"
    
    def get_device_storage_info(self, device_id: str) -> Dict[str, str]:
        """Obtém informações de armazenamento do dispositivo"""
        try:
            result = subprocess.run(
                self.get_adb_command('-s', device_id, 'shell', 'df', '/sdcard'),
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    data = lines[1].split()
                    if len(data) >= 4:
                        total = int(data[1]) * 1024  # KB para bytes
                        used = int(data[2]) * 1024
                        available = int(data[3]) * 1024
                        
                        return {
                            'total': self.format_bytes(total),
                            'used': self.format_bytes(used),
                            'available': self.format_bytes(available),
                            'used_percent': f"{(used/total)*100:.1f}%"
                        }
        except Exception:
            pass
        
        return {
            'total': 'Desconhecido',
            'used': 'Desconhecido', 
            'available': 'Desconhecido',
            'used_percent': 'Desconhecido'
        }
    
    def format_bytes(self, bytes_value: int) -> str:
        """Formata bytes em unidades legíveis"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
    
    def test_device_recording_capability(self, device_id: str) -> Tuple[bool, str]:
        """Testa se o dispositivo suporta gravação de tela"""
        try:
            # Testar comando screenrecord com help
            result = subprocess.run(
                self.get_adb_command('-s', device_id, 'shell', 'screenrecord', '--help'),
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                return True, "Suporte completo"
            else:
                return False, "Comando screenrecord não encontrado"
                
        except Exception as e:
            return False, f"Erro ao testar: {str(e)}"
    
    def get_recording_capabilities(self, device_id: str) -> Dict[str, any]:
        """Obtém capacidades de gravação do dispositivo"""
        capabilities = {
            'max_resolution': 'Desconhecida',
            'supported_formats': ['mp4'],
            'max_bitrate': '20M',
            'max_duration': 180,  # segundos
            'has_audio': False
        }
        
        try:
            # Verificar versão SDK para determinar capacidades
            sdk = self.get_device_property(device_id, 'ro.build.version.sdk')
            if sdk.isdigit():
                sdk_int = int(sdk)
                
                # Android 4.4+ (API 19+) suporta screenrecord básico
                if sdk_int >= 19:
                    capabilities['supported_formats'] = ['mp4']
                    
                # Android 5.0+ (API 21+) suporta mais opções
                if sdk_int >= 21:
                    capabilities['max_bitrate'] = '20M'
                    capabilities['max_duration'] = 180
                    
                # Android 10+ (API 29+) suporta áudio interno em alguns dispositivos
                if sdk_int >= 29:
                    capabilities['has_audio'] = True
        
        except Exception:
            pass
        
        return capabilities
    
    def connect_wifi_adb(self, ip_address: str, port: int = 5555) -> Tuple[bool, str]:
        """Conecta ao dispositivo via Wi-Fi"""
        try:
            # Primeiro, tentar conectar
            result = subprocess.run(
                self.get_adb_command('connect', f'{ip_address}:{port}'),
                capture_output=True, text=True, timeout=15
            )
            
            if 'connected' in result.stdout.lower():
                return True, f"Conectado via Wi-Fi: {ip_address}:{port}"
            else:
                return False, f"Falha na conexão: {result.stdout.strip()}"
                
        except Exception as e:
            return False, f"Erro ao conectar: {str(e)}"
    
    def disconnect_device(self, device_id: str) -> bool:
        """Desconecta dispositivo específico"""
        try:
            result = subprocess.run(
                self.get_adb_command('disconnect', device_id),
                capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def enable_wifi_adb(self, device_id: str, port: int = 5555) -> Tuple[bool, str]:
        """Ativa ADB via Wi-Fi no dispositivo (requer conexão USB primeiro)"""
        try:
            result = subprocess.run(
                self.get_adb_command('-s', device_id, 'tcpip', str(port)),
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                return True, f"ADB via Wi-Fi ativado na porta {port}"
            else:
                return False, f"Erro: {result.stderr.strip()}"
                
        except Exception as e:
            return False, f"Erro ao ativar Wi-Fi ADB: {str(e)}"
    
    def get_device_ip(self, device_id: str) -> Optional[str]:
        """Obtém IP do dispositivo na rede Wi-Fi"""
        try:
            result = subprocess.run(
                self.get_adb_command('-s', device_id, 'shell', 'ip', 'addr', 'show', 'wlan0'),
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                # Procurar por padrão IP
                ip_match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)/', result.stdout)
                if ip_match:
                    return ip_match.group(1)
        except Exception:
            pass
        
        return None
    
    def save_device_profiles(self, devices: List[Dict], filename: str = "device_profiles.json"):
        """Salva perfis de dispositivos em arquivo"""
        try:
            with open(filename, 'w') as f:
                json.dump(devices, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
    
    def load_device_profiles(self, filename: str = "device_profiles.json") -> List[Dict]:
        """Carrega perfis de dispositivos de arquivo"""
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except Exception:
            return []


class RecordingPresets:
    """Presets de configuração para diferentes tipos de gravação"""
    
    PRESETS = {
        'alta_qualidade': {
            'name': 'Alta Qualidade',
            'resolution': '1920x1080',
            'bitrate': '12',
            'fps': '30',
            'description': 'Melhor qualidade, arquivos grandes'
        },
        'qualidade_media': {
            'name': 'Qualidade Média',
            'resolution': '1280x720',
            'bitrate': '8',
            'fps': '30',
            'description': 'Boa qualidade, tamanho equilibrado'
        },
        'qualidade_baixa': {
            'name': 'Qualidade Baixa',
            'resolution': '854x480',
            'bitrate': '4',
            'fps': '24',
            'description': 'Menor qualidade, arquivos pequenos'
        },
        'streaming': {
            'name': 'Para Streaming',
            'resolution': '1280x720',
            'bitrate': '6',
            'fps': '60',
            'description': 'Otimizado para transmissão'
        },
        'tutorial': {
            'name': 'Tutorial/Demo',
            'resolution': '1920x1080',
            'bitrate': '8M',
            'fps': '24',
            'description': 'Boa qualidade para demonstrações'
        }
    }
    
    @staticmethod
    def get_preset_names() -> List[str]:
        """Retorna lista de nomes dos presets"""
        return [preset['name'] for preset in RecordingPresets.PRESETS.values()]
    
    @staticmethod
    def get_preset_by_name(preset_name: str) -> Optional[Dict]:
        """Obtém preset por nome"""
        for preset in RecordingPresets.PRESETS.values():
            if preset['name'] == preset_name:
                return preset
        return None
    
    @staticmethod
    def apply_preset(preset_name: str, app_instance):
        """Aplica preset às configurações do aplicativo"""
        preset = RecordingPresets.get_preset_by_name(preset_name)
        if preset and app_instance:
            app_instance.resolution_var.set(preset['resolution'])
            app_instance.bitrate_var.set(preset['bitrate'].replace('M', ''))
            app_instance.fps_var.set(preset['fps'])
            app_instance.log_message(f"Preset aplicado: {preset['name']}")

# Instância global para uso simplificado
adb_utils = ADBUtils() 