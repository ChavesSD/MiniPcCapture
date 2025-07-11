from flask import Flask, Response, request
import mss
import mss.tools
import io
from PIL import Image
import socket
import logging
import os
import signal
import threading
import sys

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Variáveis globais para controle
MONITOR_INDEX = 0  # 0 = monitor principal, 1 = secundário
should_stop = False
sct = None
stream_thread = None

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "IP não encontrado"

def init_screen_capture():
    try:
        global sct
        sct = mss.mss()
        logger.info(f"Monitores disponíveis: {len(sct.monitors)}")
        
        # Ajusta o monitor secundário para ter dimensões próprias
        if MONITOR_INDEX == 1 and len(sct.monitors) == 1:
            # Cria um monitor virtual secundário
            sct.monitors.append({
                'top': 0,
                'left': sct.monitors[0]['width'],  # Posiciona à direita do monitor principal
                'width': 1920,
                'height': 1080,
                'name': 'Monitor 2'
            })
        
        for i, monitor in enumerate(sct.monitors):
            logger.info(f"Monitor {i}: {monitor}")
        return True
    except Exception as e:
        logger.error(f"Erro ao inicializar captura de tela: {e}")
        return False

def capture_screen():
    try:
        # Se for monitor secundário e não existir, retorna tela preta
        if MONITOR_INDEX == 1 and len(sct.monitors) == 1:
            img = Image.new('RGB', (1920, 1080), color='black')
        else:
            screen = sct.grab(sct.monitors[MONITOR_INDEX])
            img = Image.frombytes("RGB", screen.size, screen.rgb)
        
        img_byte_array = io.BytesIO()
        img.save(img_byte_array, format='JPEG', quality=70)
        return img_byte_array.getvalue()
    except Exception as e:
        logger.error(f"Erro na captura: {e}")
        return None

def gen_frames():
    global should_stop
    if not init_screen_capture():
        return

    while not should_stop:
        try:
            frame = capture_screen()
            if frame:
                yield (b'--frame\r\n'
                      b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except Exception as e:
            logger.error(f"Erro no streaming: {e}")
            break

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/shutdown', methods=['GET'])
def shutdown():
    global should_stop
    try:
        should_stop = True
        logger.info("Encerrando servidor...")
        # Força o encerramento do processo após 1 segundo
        threading.Timer(1.0, lambda: os.kill(os.getpid(), signal.SIGTERM)).start()
        return 'Servidor encerrado'
    except Exception as e:
        logger.error(f"Erro ao encerrar: {e}")
        return 'Erro ao encerrar servidor', 500

@app.route('/monitor/<int:index>')
def set_monitor(index):
    global MONITOR_INDEX
    MONITOR_INDEX = index
    return f'Monitor alterado para {index}'

@app.route('/')
def index():
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

if __name__ == '__main__':
    ip = get_local_ip()
    logger.info(f"Iniciando servidor em http://{ip}:5000")
    logger.info("Pressione Ctrl+C para encerrar")
    
    try:
        if init_screen_capture():
            app.run(host='0.0.0.0', port=5000, debug=True)
        else:
            logger.error("Não foi possível inicializar a captura de tela")
    except Exception as e:
        logger.error(f"Erro ao iniciar servidor: {e}")
    finally:
        if sct:
            sct.close() 