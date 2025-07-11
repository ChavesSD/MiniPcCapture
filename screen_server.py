from flask import Flask, Response, request
import mss
import mss.tools
import io
from PIL import Image, ImageDraw
import socket
import logging
import os
import signal
import threading
import sys
from ctypes import windll, Structure, c_long, byref

# Configurar logging
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(levelname)s - %(message)s')

# Variáveis globais
should_stop = False
monitor_index = 1  # Padrão: monitor secundário

# Processa argumentos de linha de comando
if len(sys.argv) > 1:
    try:
        monitor_index = int(sys.argv[1])
        logging.info(f"Usando monitor {monitor_index}")
    except ValueError:
        logging.error("Índice do monitor inválido, usando padrão (1)")

# Estrutura para armazenar coordenadas do cursor
class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]

def get_cursor_position():
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    return (pt.x, pt.y)

def draw_cursor(image):
    try:
        # Obtém a posição atual do cursor
        cursor_pos = get_cursor_position()
        
        # Cria um objeto ImageDraw para desenhar sobre a imagem
        draw = ImageDraw.Draw(image)
        
        # Desenha um círculo vermelho na posição do cursor
        cursor_radius = 5
        x, y = cursor_pos
        draw.ellipse([x - cursor_radius, y - cursor_radius, 
                     x + cursor_radius, y + cursor_radius], 
                    fill='red', outline='white')
        
        return image
    except Exception as e:
        logging.error(f"Erro ao desenhar cursor: {e}")
        return image

def capture_screen():
    with mss.mss() as sct:
        try:
            # Lista todos os monitores disponíveis
            logging.debug(f"Monitores disponíveis: {len(sct.monitors)}")
            for i, m in enumerate(sct.monitors):
                logging.debug(f"Monitor {i}: {m}")
            
            # Tenta capturar o monitor selecionado
            monitor = sct.monitors[monitor_index]
            logging.debug(f"Capturando monitor {monitor_index}: {monitor}")
            
            # Captura a tela
            screenshot = sct.grab(monitor)
            
            # Converte para imagem PIL
            img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
            
            # Desenha o cursor na imagem
            img = draw_cursor(img)
            
            # Converte para bytes
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG', quality=70)
            img_byte_arr = img_byte_arr.getvalue()
            
            return img_byte_arr
            
        except IndexError:
            logging.error(f"Monitor {monitor_index} não encontrado")
            return None
        except Exception as e:
            logging.error(f"Erro ao capturar tela: {e}")
            return None

app = Flask(__name__)

def shutdown_server():
    """Função para desligar o servidor Flask"""
    global should_stop
    should_stop = True
    logging.info("Solicitação de desligamento recebida")
    
    # Obtém o ID do processo atual
    pid = os.getpid()
    
    # Agenda o encerramento do processo após 1 segundo
    def delayed_shutdown():
        logging.info("Encerrando servidor...")
        os.kill(pid, signal.SIGTERM)
    
    threading.Timer(1.0, delayed_shutdown).start()

@app.route('/shutdown', methods=['POST'])
def shutdown():
    """Rota para desligar o servidor"""
    shutdown_server()
    return 'Servidor está sendo encerrado...'

def gen_frames():
    """Gerador de frames para o stream MJPEG"""
    global should_stop
    while not should_stop:
        frame = capture_screen()
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            logging.error("Falha ao capturar frame")
            break

@app.route('/')
def index():
    """Página principal com visualização do stream"""
    logging.info("Página inicial acessada")
    return """
    <html>
    <head>
        <title>Segunda Tela PC</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { 
                margin: 0; 
                background: black;
                overflow: hidden; 
            }
            img { 
                width: 100vw; 
                height: 100vh; 
                object-fit: contain;
                display: block;
            }
            #status {
                position: fixed;
                top: 10px;
                left: 10px;
                color: white;
                background: rgba(0,0,0,0.5);
                padding: 5px 10px;
                border-radius: 5px;
                font-family: Arial;
                z-index: 1000;
            }
            #error {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                color: white;
                background: rgba(255,0,0,0.7);
                padding: 20px;
                border-radius: 10px;
                font-family: Arial;
                text-align: center;
                display: none;
            }
        </style>
    </head>
    <body>
        <div id="status">Conectando...</div>
        <div id="error">Erro na conexão!<br>Tentando reconectar...</div>
        <img src="/video_feed" onerror="onError()" onload="onLoad()"/>
        <script>
            let errorCount = 0;
            
            function onError() {
                errorCount++;
                document.getElementById('status').innerHTML = 'Erro na conexão!';
                document.getElementById('status').style.background = 'rgba(255,0,0,0.5)';
                document.getElementById('error').style.display = 'block';
                
                if (errorCount < 5) {
                    setTimeout(() => {
                        // Tenta reconectar
                        document.querySelector('img').src = '/video_feed?' + new Date().getTime();
                    }, 1000);
                }
            }
            
            function onLoad() {
                errorCount = 0;
                document.getElementById('status').innerHTML = 'Conectado';
                document.getElementById('status').style.background = 'rgba(0,255,0,0.5)';
                document.getElementById('error').style.display = 'none';
            }
        </script>
    </body>
    </html>
    """

@app.route('/video_feed')
def video_feed():
    """Gera o stream de vídeo"""
    logging.info("Nova conexão recebida para o stream de vídeo")
    return Response(gen_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    try:
        # Obtém o IP da máquina
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        logging.info(f"Iniciando servidor em {local_ip}:5000")
        
        # Inicia o servidor
        app.run(host=local_ip, port=5000, threaded=True)
    except Exception as e:
        logging.error(f"Erro ao iniciar servidor: {e}") 