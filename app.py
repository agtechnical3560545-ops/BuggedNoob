from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os
import sys
import threading
import asyncio
import queue
import time
from typing import Optional
import json

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
CORS(app)

# Global variables
bot_running = False
bot_thread = None
web_command_queue = queue.Queue()
bot_connected = True  # Set to True for testing
command_stats = {}
bot_start_time = time.time()
PORT = int(os.environ.get('PORT', 5000))
WEB_SERVER_TOKEN = 'AP_TCP_BOT_WEB_2024'

# Home route - Serve the web interface
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    """API endpoint for bot status"""
    try:
        queue_size = web_command_queue.qsize()
    except:
        queue_size = 0
    
    uptime = int(time.time() - bot_start_time)
    
    return jsonify({
        'status': 'online' if bot_connected else 'offline',
        'connected': bot_connected,
        'queue_size': queue_size,
        'uptime': uptime,
        'commands_processed': sum(command_stats.values()) if command_stats else 0,
        'server': 'Render.com',
        'owner': '★VoiDReaP★',
        'version': '2.0'
    })

@app.route('/api/command', methods=['POST'])
def api_command():
    """API endpoint to receive commands"""
    global command_stats, bot_connected
    
    try:
        # Check if request has JSON data
        if not request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        
        # Debug: Print received data
        print(f"Received data: {data}")
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No JSON data received'
            }), 400
        
        # Validate token
        token = data.get('token')
        if token != WEB_SERVER_TOKEN:
            print(f"Token mismatch. Expected: {WEB_SERVER_TOKEN}, Got: {token}")
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
        
        sender = data.get('sender', 'API User')
        
        # Add command to queue
        try:
            web_command_queue.put({
                'command': command,
                'sender': sender,
                'timestamp': time.time()
            })
            
            # Track command stats
            cmd_key = command.split()[0] if ' ' in command else command
            if cmd_key in command_stats:
                command_stats[cmd_key] += 1
            else:
                command_stats[cmd_key] = 1
            
            print(f"Command queued: {command} from {sender}")
            
            return jsonify({
                'status': 'success',
                'message': 'Command queued successfully',
                'queue_position': web_command_queue.qsize(),
                'bot_connected': bot_connected,
                'command': command
            })
            
        except Exception as e:
            print(f"Queue error: {e}")
            return jsonify({
                'status': 'error',
                'message': f'Failed to queue command: {str(e)}'
            }), 500
        
    except Exception as e:
        print(f"API error: {e}")
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
                'token': WEB_SERVER_TOKEN,
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
    return jsonify({'status': 'healthy', 'bot_running': bot_running}), 200

# Test endpoint
@app.route('/api/test')
def test_api():
    return jsonify({
        'status': 'success',
        'message': 'API is working',
        'timestamp': time.time(),
        'queue_size': web_command_queue.qsize()
    })

async def process_web_commands():
    """Process commands from web interface"""
    global bot_connected
    
    print("Web command processor started")
    
    while True:
        try:
            # Check for new commands
            if not web_command_queue.empty():
                command_data = web_command_queue.get()
                print(f"Processing web command: {command_data['command']} from {command_data['sender']}")
                
                # Here you would implement actual command processing
                # For now, simulate processing
                print(f"Executing: {command_data['command']}")
                
                # Simulate command execution
                if command_data['command'].startswith('/like/'):
                    print(f"Sending likes...")
                elif command_data['command'].startswith('/x/'):
                    print(f"Joining squad...")
                elif command_data['command'].startswith('/e '):
                    print(f"Sending emote...")
                
                web_command_queue.task_done()
            
            await asyncio.sleep(0.5)  # Small delay
            
        except Exception as e:
            print(f"Error in web command processor: {e}")
            await asyncio.sleep(1)

# Bot simulation functions
async def simulate_bot_connection():
    """Simulate bot connection for testing"""
    global bot_connected
    
    print("Bot simulation started")
    bot_connected = True
    
    # Simulate processing commands from queue
    while True:
        try:
            if not web_command_queue.empty():
                # Don't actually process here, let process_web_commands handle it
                pass
            await asyncio.sleep(1)
        except Exception as e:
            print(f"Bot simulation error: {e}")
            await asyncio.sleep(5)

async def StarTinG():
    """Main bot starting function"""
    print("Starting bot simulation...")
    
    # Start command processor
    command_processor = asyncio.create_task(process_web_commands())
    
    # Start bot simulation
    bot_sim = asyncio.create_task(simulate_bot_connection())
    
    print("Bot is now running and accepting commands")
    print(f"Web interface: http://localhost:{PORT}")
    print(f"API Token: {WEB_SERVER_TOKEN}")
    print(f"Owner: ★VoiDReaP★")
    
    await asyncio.gather(command_processor, bot_sim)

def run_bot():
    """Run the bot in a separate thread"""
    global bot_running, bot_connected
    
    try:
        bot_running = True
        print("Starting bot in separate thread...")
        asyncio.run(StarTinG())
    except Exception as e:
        print(f"Bot thread error: {e}")
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
    print("=" * 60)
    print("AP TCP BOT v2.0 - Web Interface")
    print("Owner: ★VoiDReaP★")
    print("=" * 60)
    
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Create a better index.html with working JavaScript
    index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AP TCP BOT v2.0 Control Panel</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
        }
        
        header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid rgba(255, 255, 255, 0.1);
        }
        
        h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            color: #00ff88;
            text-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
        }
        
        .subtitle {
            color: #88ffaa;
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }
        
        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
        }
        
        .panel {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .panel h2 {
            color: #00ccff;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .status-box {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .status-indicator {
            padding: 8px 20px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9rem;
        }
        
        .status-online {
            background: rgba(0, 255, 136, 0.2);
            color: #00ff88;
            border: 1px solid #00ff88;
        }
        
        .status-offline {
            background: rgba(255, 0, 0, 0.2);
            color: #ff4444;
            border: 1px solid #ff4444;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .stat-item {
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 1.5rem;
            font-weight: bold;
            color: #00ccff;
        }
        
        .stat-label {
            font-size: 0.9rem;
            opacity: 0.8;
        }
        
        .command-input {
            margin-top: 20px;
        }
        
        .input-group {
            margin-bottom: 15px;
        }
        
        label {
            display: block;
            margin-bottom: 5px;
            color: #88ffaa;
        }
        
        input {
            width: 100%;
            padding: 12px;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 6px;
            color: white;
            font-size: 1rem;
        }
        
        input:focus {
            outline: none;
            border-color: #00ccff;
            box-shadow: 0 0 10px rgba(0, 204, 255, 0.3);
        }
        
        button {
            background: linear-gradient(135deg, #00ccff 0%, #0066ff 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 6px;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
            font-weight: bold;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 102, 255, 0.4);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        .btn-clear {
            background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%);
            margin-top: 10px;
        }
        
        .logs {
            background: rgba(0, 0, 0, 0.5);
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
            max-height: 300px;
            overflow-y: auto;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.9rem;
        }
        
        .log-entry {
            padding: 8px;
            margin: 5px 0;
            border-left: 3px solid #00ccff;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 4px;
        }
        
        .log-time {
            color: #ffcc00;
        }
        
        .log-success {
            border-left-color: #00ff88;
        }
        
        .log-error {
            border-left-color: #ff4444;
        }
        
        .log-info {
            border-left-color: #00ccff;
        }
        
        footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            color: #88ffaa;
            font-size: 0.9rem;
        }
        
        .developer {
            color: #ffcc00;
            font-weight: bold;
        }
        
        .host-info {
            margin-top: 10px;
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>AP TCP BOT v2.0</h1>
            <div class="subtitle">Free Fire Bot Control Panel | Web Interface</div>
        </header>
        
        <div class="main-content">
            <div class="panel">
                <h2>Bot Status & Control</h2>
                
                <div class="status-box">
                    <div>
                        <div id="statusText">Checking status...</div>
                        <div id="serverInfo" style="font-size: 0.9rem; opacity: 0.8; margin-top: 5px;"></div>
                    </div>
                    <div id="statusIndicator" class="status-indicator status-offline">OFFLINE</div>
                </div>
                
                <div class="stats">
                    <div class="stat-item">
                        <div class="stat-value" id="queueSize">0</div>
                        <div class="stat-label">Queue Size</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="uptime">0s</div>
                        <div class="stat-label">Uptime</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="commandsProcessed">0</div>
                        <div class="stat-label">Commands</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="version">2.0</div>
                        <div class="stat-label">Version</div>
                    </div>
                </div>
                
                <div class="command-input">
                    <h2>Send Command</h2>
                    
                    <div class="input-group">
                        <label for="senderName">Your Name</label>
                        <input type="text" id="senderName" placeholder="Enter your name" value="Web User">
                    </div>
                    
                    <div class="input-group">
                        <label for="commandInput">Command</label>
                        <input type="text" id="commandInput" placeholder="Enter command (e.g., /like/123456789)" value="/x/8288603">
                    </div>
                    
                    <button onclick="sendCommand()">Send Command</button>
                    <button class="btn-clear" onclick="clearLogs()">Clear Logs</button>
                    
                    <div style="margin-top: 20px; font-size: 0.9rem; opacity: 0.8;">
                        <strong>Available Commands:</strong><br>
                        /like/[UID], /x/[TEAM], /e [UID] [EMOTE], /solo, /s, /info [UID], etc.
                    </div>
                </div>
            </div>
            
            <div class="panel">
                <h2>Command Logs</h2>
                <div class="logs" id="commandLogs">
                    <div class="log-entry log-info">
                        <span class="log-time">[Control panel initialized]</span>
                    </div>
                </div>
                
                <div style="margin-top: 20px;">
                    <h3>Quick Commands</h3>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px;">
                        <button onclick="quickCommand('/like/123456789')" style="width: auto; padding: 8px 15px;">Like</button>
                        <button onclick="quickCommand('/x/8288603')" style="width: auto; padding: 8px 15px;">Join Squad</button>
                        <button onclick="quickCommand('/solo')" style="width: auto; padding: 8px 15px;">Solo</button>
                        <button onclick="quickCommand('/s')" style="width: auto; padding: 8px 15px;">Speed Boost</button>
                    </div>
                </div>
            </div>
        </div>
        
        <footer>
            <div class="developer">Developed with 👍 by ★VoiDReaP★</div>
            <div class="host-info">
                👍 AP TCP BOT v2.0 | 💬 Hosted on Render.com
            </div>
            <div style="margin-top: 10px; font-size: 0.8rem; opacity: 0.7;">
                This interface is for controlling Free Fire bot via web. Use reasonable.
            </div>
        </footer>
    </div>
    
    <script>
        let logs = [];
        
        // Function to add log entry
        function addLog(message, type = 'info') {
            const now = new Date();
            const timeString = `[${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}]`;
            
            const logEntry = {
                time: timeString,
                message: message,
                type: type
            };
            
            logs.unshift(logEntry); // Add to beginning
            
            // Update logs display
            const logsContainer = document.getElementById('commandLogs');
            const logDiv = document.createElement('div');
            logDiv.className = `log-entry log-${type}`;
            logDiv.innerHTML = `<span class="log-time">${timeString}</span> ${message}`;
            
            logsContainer.insertBefore(logDiv, logsContainer.firstChild);
            
            // Keep only last 50 logs
            if (logs.length > 50) {
                logs.pop();
                if (logsContainer.children.length > 50) {
                    logsContainer.removeChild(logsContainer.lastChild);
                }
            }
        }
        
        // Function to clear logs
        function clearLogs() {
            logs = [];
            document.getElementById('commandLogs').innerHTML = 
                '<div class="log-entry log-info">' +
                '<span class="log-time">[Logs cleared]</span>' +
                '</div>';
            addLog('Logs cleared', 'info');
        }
        
        // Function to update status
        async function updateStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                // Update status indicator
                const statusIndicator = document.getElementById('statusIndicator');
                const statusText = document.getElementById('statusText');
                
                if (data.connected) {
                    statusIndicator.className = 'status-indicator status-online';
                    statusIndicator.textContent = 'ONLINE';
                    statusText.textContent = 'Bot is online and ready';
                } else {
                    statusIndicator.className = 'status-indicator status-offline';
                    statusIndicator.textContent = 'OFFLINE';
                    statusText.textContent = 'Bot is offline';
                }
                
                // Update server info
                document.getElementById('serverInfo').textContent = 
                    `${data.server} | Owner: ${data.owner}`;
                
                // Update stats
                document.getElementById('queueSize').textContent = data.queue_size;
                document.getElementById('uptime').textContent = `${data.uptime}s`;
                document.getElementById('commandsProcessed').textContent = data.commands_processed;
                document.getElementById('version').textContent = data.version;
                
            } catch (error) {
                console.error('Failed to fetch status:', error);
                document.getElementById('statusIndicator').className = 'status-indicator status-offline';
                document.getElementById('statusIndicator').textContent = 'ERROR';
                document.getElementById('statusText').textContent = 'Failed to fetch status';
                addLog('Failed to fetch status: ' + error.message, 'error');
            }
        }
        
        // Function to send command
        async function sendCommand() {
            const commandInput = document.getElementById('commandInput');
            const senderInput = document.getElementById('senderName');
            const command = commandInput.value.trim();
            const sender = senderInput.value.trim() || 'Web User';
            
            if (!command) {
                alert('Please enter a command');
                return;
            }
            
            addLog(`Sending command: ${command}`, 'info');
            
            try {
                const response = await fetch('/api/command', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        token: 'AP_TCP_BOT_WEB_2024',
                        command: command,
                        sender: sender
                    })
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    addLog(`Command sent successfully: ${command}`, 'success');
                    commandInput.value = ''; // Clear input
                } else {
                    addLog(`Command failed: ${data.message}`, 'error');
                }
                
                // Update status after sending command
                updateStatus();
                
            } catch (error) {
                console.error('Error sending command:', error);
                addLog(`Command failed: ${error.message}`, 'error');
            }
        }
        
        // Function for quick commands
        function quickCommand(command) {
            document.getElementById('commandInput').value = command;
            sendCommand();
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            addLog('Control panel initialized', 'info');
            updateStatus();
            
            // Update status every 5 seconds
            setInterval(updateStatus, 5000);
            
            // Allow pressing Enter to send command
            document.getElementById('commandInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendCommand();
                }
            });
        });
    </script>
</body>
</html>"""
    
    # Save index.html
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    # Start bot in background
    start_bot()
    
    print(f"\n✅ Bot started successfully!")
    print(f"🌐 Web Interface: http://localhost:{PORT}")
    print(f"🔑 API Token: {WEB_SERVER_TOKEN}")
    print(f"👑 Owner: ★VoiDReaP★")
    print(f"📊 Status API: http://localhost:{PORT}/api/status")
    print(f"📚 Help: http://localhost:{PORT}/api/help")
    print(f"❤️  Developed with ❤️ by ★VoiDReaP★")
    print("\n" + "=" * 60)
    
    # Run Flask app
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

if __name__ == '__main__':
    # Install required packages if not present
    try:
        from flask import Flask
        from flask_cors import CORS
    except ImportError:
        print("Installing required packages...")
        os.system("pip install flask flask-cors")
    
    main()
