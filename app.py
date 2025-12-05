from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os
import sys
import threading
import asyncio
import queue
import time
from typing import Optional

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
CORS(app)

# Global variables
bot_running = False
bot_thread = None
web_command_queue = None
bot_connected = False
command_stats = {}
bot_start_time = time.time()

# Home route - Serve the web interface
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    """API endpoint for bot status"""
    queue_size = 0
    if web_command_queue:
        try:
            queue_size = web_command_queue.qsize()
        except:
            queue_size = 0
    
    return jsonify({
        'status': 'online' if bot_connected else 'offline',
        'connected': bot_connected,
        'queue_size': queue_size,
        'uptime': time.time() - bot_start_time,
        'commands_processed': sum(command_stats.values()) if command_stats else 0,
        'server': 'Render.com',
        'owner': '★VoiDReaP★',
        'version': '2.0'
    })

@app.route('/api/command', methods=['POST'])
def api_command():
    """API endpoint to receive commands"""
    try:
        data = request.json
        
        # Validate token (you should use environment variable in production)
        if data.get('token') != 'AP_TCP_BOT_WEB_2024':
            return jsonify({
                'status': 'error',
                'message': 'Invalid token'
            }), 403
        
        command = data.get('command', '').strip()
        if not command:
            return jsonify({
                'status': 'error',
                'message': 'No command provided'
            }), 400
        
        # If bot is not running, queue is not available
        if not bot_running or web_command_queue is None:
            return jsonify({
                'status': 'error',
                'message': 'Bot is not running'
            }), 503
        
        # Add command to queue
        try:
            web_command_queue.put({
                'command': command,
                'sender': data.get('sender', 'API User'),
                'timestamp': time.time()
            })
            
            # Track command stats
            cmd_key = command.split()[0]
            if cmd_key in command_stats:
                command_stats[cmd_key] += 1
            else:
                command_stats[cmd_key] = 1
            
            return jsonify({
                'status': 'success',
                'message': 'Command queued',
                'queue_position': web_command_queue.qsize(),
                'bot_connected': bot_connected
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Failed to queue command: {str(e)}'
            }), 500
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/help')
def api_help():
    """API documentation"""
    return jsonify({
        'service': 'AP TCP BOT Web Interface',
        'owner': '★VoiDReaP★',
        'endpoints': {
            'GET /': 'Web interface',
            'GET /api/status': 'Bot status',
            'POST /api/command': 'Send command to bot',
            'GET /api/help': 'This documentation'
        },
        'sample_request': {
            'method': 'POST',
            'url': '/api/command',
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': {
                'token': 'AP_TCP_BOT_WEB_2024',
                'command': '/like/123456789',
                'sender': 'YourName'
            }
        },
        'available_commands': [
            '/help - Show all commands',
            '/like/[UID] - Send 100 likes',
            '/e [UID] [EMOTE_ID] - Send emote',
            '/x/[TEAM_CODE] - Join squad',
            '/3, /5, /6 - Create squad',
            '/solo - Leave squad',
            '/s - Speed boost',
            '/info [UID] - Player info',
            '/clan [ID] - Clan info',
            '/visit [UID] - Send visits',
            '/ai [QUESTION] - AI chat',
            '/spam [UID] - Spam requests',
            '/ee [TEAM] [UIDs] [E] - Join+Emote+Leave'
        ]
    })

# Health check endpoint for Render
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'}), 200

async def process_web_commands():
    """Process commands from web interface"""
    global web_command_queue, bot_connected
    
    if web_command_queue is None:
        web_command_queue = queue.Queue()
    
    while True:
        try:
            # Check for new commands
            if not web_command_queue.empty():
                command_data = web_command_queue.get()
                print(f"Processing web command: {command_data['command']} from {command_data['sender']}")
                # Here you would implement actual command processing
                # For now just acknowledge
                web_command_queue.task_done()
            
            await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
        except Exception as e:
            print(f"Error in web command processor: {e}")
            await asyncio.sleep(1)

# Bot functions (placeholder implementations)
async def GeNeRaTeAccEss(uid: str, pw: str) -> tuple:
    """Generate access tokens"""
    # Placeholder implementation
    return "open_id_placeholder", "access_token_placeholder"

async def EncRypTMajoRLoGin(open_id: str, access_token: str) -> str:
    """Encrypt major login"""
    return "encrypted_data"

async def MajorLogin(encrypted_data: str) -> Optional[str]:
    """Major login"""
    # Placeholder
    return "response_data"

async def DecRypTMajoRLoGin(response: str):
    """Decrypt major login response"""
    # Placeholder class
    class AuthResponse:
        def __init__(self):
            self.url = "http://example.com"
            self.region = "region"
            self.token = "token"
            self.account_uid = "account_uid"
            self.key = "key"
            self.iv = "iv"
            self.timestamp = str(int(time.time()))
    
    return AuthResponse()

async def GetLoginData(url: str, encrypted_data: str, token: str):
    """Get login data"""
    return "login_data"

async def DecRypTLoGinDaTa(login_data: str):
    """Decrypt login data"""
    # Placeholder class
    class LoginDataResponse:
        def __init__(self):
            self.Online_IP_Port = "127.0.0.1:8080"
            self.AccountIP_Port = "127.0.0.1:8081"
            self.AccountName = "BotAccount"
    
    return LoginDataResponse()

async def xAuThSTarTuP(target: int, token: str, timestamp: int, key: str, iv: str) -> str:
    """XAuth startup"""
    return "auth_token"

async def TcPChaT(ip: str, port: str, auth_token: str, key: str, iv: str, login_data, ready_event, region: str):
    """TCP Chat handler"""
    # Simulate connection
    print(f"Connecting to chat at {ip}:{port}")
    await asyncio.sleep(2)
    bot_connected = True
    ready_event.set()
    
    # Keep connection alive
    while True:
        await asyncio.sleep(10)

async def TcPOnLine(ip: str, port: str, key: str, iv: str, auth_token: str):
    """TCP Online handler"""
    print(f"Connecting to online at {ip}:{port}")
    
    # Keep connection alive
    while True:
        await asyncio.sleep(10)

def render(text: str, colors: list = None, align: str = 'left') -> str:
    """Render text with colors and alignment"""
    # Simple implementation
    return f"\n{text.center(80) if align == 'center' else text}\n"

async def MaiiiinE():
    """Main bot function"""
    global bot_connected, web_command_queue
    
    # Initialize web command queue
    web_command_queue = queue.Queue()
    
    # Simulate bot login process (using your provided code structure)
    Uid, Pw = '4287206411', '534E8411AF1334820FF02F01EFB90E6B6BC036688E94440018AFB0290AA5EF89'
    
    open_id, access_token = await GeNeRaTeAccEss(Uid, Pw)
    if not open_id or not access_token: 
        print("Error - Invalid Account") 
        return None
    
    PyL = await EncRypTMajoRLoGin(open_id, access_token)
    MajoRLoGinResPonsE = await MajorLogin(PyL)
    if not MajoRLoGinResPonsE: 
        print("Target Account => Banned / Not Registered!") 
        return None
    
    MajoRLoGinauTh = await DecRypTMajoRLoGin(MajoRLoGinResPonsE)
    UrL = MajoRLoGinauTh.url
    print(f"URL: {UrL}")
    region = MajoRLoGinauTh.region

    ToKen = MajoRLoGinauTh.token
    TarGeT = MajoRLoGinauTh.account_uid
    key = MajoRLoGinauTh.key
    iv = MajoRLoGinauTh.iv
    timestamp = MajoRLoGinauTh.timestamp
    
    LoGinDaTa = await GetLoginData(UrL, PyL, ToKen)
    if not LoGinDaTa: 
        print("Error - Getting Ports From Login Data!") 
        return None
    LoGinDaTaUncRypTinG = await DecRypTLoGinDaTa(LoGinDaTa)
    OnLinePorTs = LoGinDaTaUncRypTinG.Online_IP_Port
    ChaTPorTs = LoGinDaTaUncRypTinG.AccountIP_Port
    OnLineiP, OnLineporT = OnLinePorTs.split(":")
    ChaTiP, ChaTporT = ChaTPorTs.split(":")
    acc_name = LoGinDaTaUncRypTinG.AccountName
    
    AutHToKen = await xAuThSTarTuP(int(TarGeT), ToKen, int(timestamp), key, iv)
    ready_event = asyncio.Event()
    
    # Start web command processor
    web_processor = asyncio.create_task(process_web_commands())
    
    task1 = asyncio.create_task(TcPChaT(ChaTiP, ChaTporT, AutHToKen, key, iv, LoGinDaTaUncRypTinG, ready_event, region))
     
    await ready_event.wait()
    await asyncio.sleep(1)
    task2 = asyncio.create_task(TcPOnLine(OnLineiP, OnLineporT, key, iv, AutHToKen))
    
    os.system('clear' if os.name == 'posix' else 'cls')
    print(render('AP TCP BOT + RENDER', colors=['white', 'blue'], align='center'))
    print('')
    print(f" - ★VoiDReaP★ Starting And Online on Target: {TarGeT} | BOT NAME: {acc_name}\n")
    print(f" - Bot Status > Good | Online!")    
    print(f" - Web Interface: Running on port 5000")    
    print(f" - API Token: AP_TCP_BOT_WEB_2024")    
    print(f" - Owner: ★VoiDReaP★")    
    await asyncio.gather(task1, task2, web_processor)

async def StarTinG():
    """Main bot starting function with restart logic"""
    while True:
        try: 
            await asyncio.wait_for(MaiiiinE(), timeout = 7 * 60 * 60)
        except asyncio.TimeoutError: 
            print("Token Expired! , Restarting")
        except Exception as e: 
            print(f"Error TCP - {e} => Restarting ...")
        await asyncio.sleep(5)  # Wait before restarting

def run_bot():
    """Run the bot in a separate thread"""
    global bot_running, bot_connected
    
    try:
        bot_running = True
        asyncio.run(StarTinG())
    except Exception as e:
        print(f"Bot error: {e}")
    finally:
        bot_running = False
        bot_connected = False

def start_bot():
    """Start bot thread"""
    global bot_thread
    if bot_thread is None or not bot_thread.is_alive():
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        print("Bot thread started")

# --------------------------------------------------
# Main execution
def main():
    """Main entry point"""
    print(f"Starting AP TCP BOT")
    print(f"Port: 5000")
    print(f"Owner: ★VoiDReaP★")
    
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Create a basic index.html if it doesn't exist
    if not os.path.exists('templates/index.html'):
        basic_html = """<!DOCTYPE html>
<html>
<head>
    <title>AP TCP BOT Web Interface</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f0f0f0; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
        h1 { color: #333; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .online { background: #d4edda; color: #155724; }
        .offline { background: #f8d7da; color: #721c24; }
        input, button { padding: 10px; margin: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>AP TCP BOT Web Interface</h1>
        <div id="status" class="status offline">Loading...</div>
        <div>
            <input type="text" id="command" placeholder="Enter command">
            <input type="text" id="sender" placeholder="Your name">
            <button onclick="sendCommand()">Send Command</button>
        </div>
        <div id="response"></div>
    </div>
    <script>
        async function updateStatus() {
            const res = await fetch('/api/status');
            const data = await res.json();
            const statusDiv = document.getElementById('status');
            statusDiv.className = data.connected ? 'status online' : 'status offline';
            statusDiv.innerHTML = `Status: ${data.status.toUpperCase()} | Queue: ${data.queue_size} | Uptime: ${Math.floor(data.uptime)}s`;
        }
        
        async function sendCommand() {
            const command = document.getElementById('command').value;
            const sender = document.getElementById('sender').value || 'API User';
            
            const res = await fetch('/api/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    token: 'AP_TCP_BOT_WEB_2024',
                    command: command,
                    sender: sender
                })
            });
            
            const data = await res.json();
            document.getElementById('response').innerHTML = JSON.stringify(data, null, 2);
        }
        
        setInterval(updateStatus, 2000);
        updateStatus();
    </script>
</body>
</html>"""
        with open('templates/index.html', 'w') as f:
            f.write(basic_html)
    
    # Start bot in background
    start_bot()
    
    # Run Flask app
    port = int(os.environ.get('PORT', 5000))
    
    print(f"\nStarting web server on port {port}")
    print(f"Web interface: http://localhost:{port}")
    print(f"API documentation: http://localhost:{port}/api/help")
    
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == '__main__':
    # Install required packages if not present
    try:
        from flask import Flask
        from flask_cors import CORS
    except ImportError:
        print("Installing required packages...")
        os.system("pip install flask flask-cors")
    
    main()
