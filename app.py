from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os
import sys
import threading
import asyncio
import aiohttp
import time

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
    return jsonify({
        'status': 'online' if bot_connected else 'offline',
        'connected': bot_connected,
        'queue_size': web_command_queue.qsize() if web_command_queue else 0,
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
        asyncio.run_coroutine_threadsafe(
            web_command_queue.put({
                'command': command,
                'sender': data.get('sender', 'API User'),
                'timestamp': time.time()
            }),
            asyncio.get_event_loop()
        )
        
        # Track command stats
        if command.split()[0] in command_stats:
            command_stats[command.split()[0]] += 1
        else:
            command_stats[command.split()[0]] = 1
        
        return jsonify({
            'status': 'success',
            'message': 'Command queued',
            'queue_position': web_command_queue.qsize(),
            'bot_connected': bot_connected
        })
        
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

def run_bot():
    """Run the bot in a separate thread"""
    global bot_running, web_command_queue, bot_connected
    
    try:
        # Import your bot here
        from your_bot_file import main as bot_main
        bot_running = True
        
        # Run the bot
        bot_main()
        
    except ImportError:
        print("Bot module not found. Running in web-only mode.")
    except Exception as e:
        print(f"Bot error: {e}")
    finally:
        bot_running = False

def start_bot():
    """Start bot thread"""
    global bot_thread
    if bot_thread is None or not bot_thread.is_alive():
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        print("Bot thread started")

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Move index.html to templates if it exists in root
    if os.path.exists('index.html'):
        os.rename('index.html', 'templates/index.html')
    
    # Start bot in background
    # Uncomment the next line if you want bot to auto-start
    # start_bot()
    
    # Get port from environment (Render provides this)
    port = int(os.environ.get('PORT', 5000))
    
    # Run Flask app
    print(f"Starting web server on port {port}")
    print(f"Web interface: http://localhost:{port}")
    print(f"API documentation: http://localhost:{port}/api/help")
    print(f"Owner: ★VoiDReaP★")
    
    app.run(host='0.0.0.0', port=port, debug=False)
Uid , Pw = '4287206411','534E8411AF1334820FF02F01EFB90E6B6BC036688E94440018AFB0290AA5EF89'

    open_id , access_token = await GeNeRaTeAccEss(Uid , Pw)
    if not open_id or not access_token: 
        print("Error - Invalid Account") 
        return None
    
    PyL = await EncRypTMajoRLoGin(open_id , access_token)
    MajoRLoGinResPonsE = await MajorLogin(PyL)
    if not MajoRLoGinResPonsE: 
        print("Target Account => Banned / Not Registered!") 
        return None
    
    MajoRLoGinauTh = await DecRypTMajoRLoGin(MajoRLoGinResPonsE)
    UrL = MajoRLoGinauTh.url
    print(UrL)
    region = MajoRLoGinauTh.region

    ToKen = MajoRLoGinauTh.token
    TarGeT = MajoRLoGinauTh.account_uid
    key = MajoRLoGinauTh.key
    iv = MajoRLoGinauTh.iv
    timestamp = MajoRLoGinauTh.timestamp
    
    LoGinDaTa = await GetLoginData(UrL , PyL , ToKen)
    if not LoGinDaTa: 
        print("Error - Getting Ports From Login Data!") 
        return None
    LoGinDaTaUncRypTinG = await DecRypTLoGinDaTa(LoGinDaTa)
    OnLinePorTs = LoGinDaTaUncRypTinG.Online_IP_Port
    ChaTPorTs = LoGinDaTaUncRypTinG.AccountIP_Port
    OnLineiP , OnLineporT = OnLinePorTs.split(":")
    ChaTiP , ChaTporT = ChaTPorTs.split(":")
    acc_name = LoGinDaTaUncRypTinG.AccountName
    
    AutHToKen = await xAuThSTarTuP(int(TarGeT) , ToKen , int(timestamp) , key , iv)
    ready_event = asyncio.Event()
    
    # Start web command processor
    web_processor = asyncio.create_task(process_web_commands())
    
    task1 = asyncio.create_task(TcPChaT(ChaTiP, ChaTporT , AutHToKen , key , iv , LoGinDaTaUncRypTinG , ready_event ,region))
     
    await ready_event.wait()
    await asyncio.sleep(1)
    task2 = asyncio.create_task(TcPOnLine(OnLineiP , OnLineporT , key , iv , AutHToKen))
    
    os.system('clear')
    print(render('AP TCP BOT + RENDER', colors=['white', 'blue'], align='center'))
    print('')
    print(f" - ★VoiDReaP★ Starting And Online on Target: {TarGeT} | BOT NAME: {acc_name}\n")
    print(f" - Bot Status > Good | Online!")    
    print(f" - Render URL: {RENDER_URL}")    
    print(f" - Web Server Port: {PORT}")    
    print(f" - API Token: {WEB_SERVER_TOKEN}")    
    print(f" - Owner: ★VoiDReaP★")    
    await asyncio.gather(task1 , task2, web_processor)
    
async def StarTinG():
    while True:
        try: 
            await asyncio.wait_for(MaiiiinE() , timeout = 7 * 60 * 60)
        except asyncio.TimeoutError: 
            print("Token Expired! , Restarting")
        except Exception as e: 
            print(f"Error TCP - {e} => Restarting ...")

# --------------------------------------------------
# Main execution
def main():
    """Main entry point for Render.com"""
    print(f"Starting AP TCP BOT on Render.com")
    print(f"URL: {RENDER_URL}")
    print(f"Port: {PORT}")
    print(f"Owner: ★VoiDReaP★")
    
    # Start Flask web server in a separate thread
    import threading
    flask_thread = threading.Thread(
        target=lambda: app.run(
            host='0.0.0.0',
            port=PORT,
            debug=False,
            use_reloader=False
        ),
        daemon=True
    )
    flask_thread.start()
    
    # Start the bot
    asyncio.run(StarTinG())

if __name__ == '__main__':
    # Install required packages if not present
    try:
        from flask import Flask
        from flask_cors import CORS
    except ImportError:
        print("Installing required packages...")
        os.system("pip install flask flask-cors")
        
    main()
