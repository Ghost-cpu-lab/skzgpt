import threading
import time
from flask import Flask
import logging

# Configurar logging do Flask para ser menos verboso
flask_log = logging.getLogger('werkzeug')
flask_log.setLevel(logging.WARNING)

app = Flask(__name__)

# Configurações otimizadas para UptimeRobot
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Sem cache
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False  # JSON compacto

@app.route('/')
def home():
    """Endpoint principal para verificar se o bot está online"""
    return '''
    <html>
        <head>
            <title>Discord Bot - Sistema de Créditos</title>
            <meta charset="UTF-8">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    min-height: 100vh;
                }
                .container {
                    background: rgba(255,255,255,0.1);
                    padding: 30px;
                    border-radius: 15px;
                    backdrop-filter: blur(10px);
                    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
                }
                .status {
                    display: inline-block;
                    padding: 10px 20px;
                    background: #2ecc71;
                    border-radius: 25px;
                    font-weight: bold;
                }
                .feature {
                    background: rgba(255,255,255,0.05);
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 8px;
                    border-left: 4px solid #2ecc71;
                }
                h1 { text-align: center; margin-bottom: 30px; }
                h3 { color: #2ecc71; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 Discord Bot - Sistema de Créditos</h1>
                
                <div style="text-align: center; margin: 30px 0;">
                    <span class="status">🟢 ONLINE</span>
                </div>
                
                <h3>📋 Funcionalidades Ativas:</h3>
                
                <div class="feature">
                    <strong>💰 Sistema de Créditos Automático</strong><br>
                    Monitora o canal de vendas e adiciona créditos automaticamente
                </div>
                
                <div class="feature">
                    <strong>🛍️ Loja de Recompensas</strong><br>
                    Usuários podem trocar créditos por descontos e contas grátis
                </div>
                
                <div class="feature">
                    <strong>📊 Comandos Slash</strong><br>
                    /saldo, /loja, /resgatar, /preco e comandos administrativos
                </div>
                
                <div class="feature">
                    <strong>🔒 Persistência de Dados</strong><br>
                    Todos os dados são salvos automaticamente em arquivos JSON
                </div>
                
                <h3>⚡ Status do Sistema:</h3>
                <div class="feature">
                    <strong>🚀 Hospedagem:</strong> Replit 24/7<br>
                    <strong>💾 Backup:</strong> Automático<br>
                    <strong>🔄 Keep-Alive:</strong> Ativo<br>
                    <strong>⏰ Uptime:</strong> Contínuo
                </div>
                
                <div style="text-align: center; margin-top: 30px; opacity: 0.8;">
                    <small>Bot desenvolvido para funcionar 24/7 na Replit</small>
                </div>
            </div>
        </body>
    </html>
    '''

@app.route('/status')
def status():
    """Endpoint de status em JSON"""
    return {
        'status': 'online',
        'service': 'discord-credits-bot',
        'uptime': True,
        'features': [
            'automatic_credits',
            'rewards_shop', 
            'slash_commands',
            'data_persistence'
        ]
    }

@app.route('/health')
def health():
    """Endpoint de health check - otimizado para UptimeRobot"""
    return {'status': 'healthy', 'timestamp': time.time(), 'uptime': 'ok'}

@app.route('/ping')
def ping():
    """Endpoint rápido para pings do UptimeRobot"""
    return 'pong'

@app.route('/uptimer')
def uptimer():
    """Endpoint específico para UptimeRobot com resposta ultra-rápida"""
    return {'bot': 'online', 'time': int(time.time())}

def run():
    """Inicia o servidor Flask em uma thread separada"""
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def keep_alive():
    """Inicia o keep-alive em background"""
    print("🌐 Iniciando servidor keep-alive na porta 5000...")
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    print("✅ Keep-alive ativo!")
