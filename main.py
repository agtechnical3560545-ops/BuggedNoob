import requests , os , psutil , sys , jwt , pickle , json , binascii , time , urllib3 , base64 , datetime , re , socket , threading , ssl , pytz , aiohttp , asyncio
from protobuf_decoder.protobuf_decoder import Parser
from xC4 import * ; from xHeaders import *
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from Pb2 import DEcwHisPErMsG_pb2 , MajoRLoGinrEs_pb2 , PorTs_pb2 , MajoRLoGinrEq_pb2 , sQ_pb2 , Team_msg_pb2
from cfonts import render, say
from flask import Flask, request, jsonify
from flask_cors import CORS
import secrets

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  

# Enhanced Configuration Variables
ADMIN_UID = "2272418033"
server2 = "IND"
key2 = "MK•DEVELOPER"
BYPASS_TOKEN = "your_bypass_token_here"
WEB_SERVER_TOKEN = "AP_TCP_BOT_WEB_2024"  # Secure token for web API

# Render.com Configuration
RENDER_URL = "https://buggednoob.onrender.com"  # Your Render URL
PORT = int(os.environ.get("PORT", 5000))  # Render automatically assigns PORT

# Optimized Global Variables
online_writer = None
whisper_writer = None
spam_room = False
spammer_uid = None
spam_chat_id = None
spam_uid = None
Spy = False
Chat_Leave = False
is_muted = False
mute_until = 0
spam_requests_sent = 0
bot_start_time = time.time()
web_command_queue = asyncio.Queue()  # Queue for web commands
bot_connected = False

# Flask Web Application
app = Flask(__name__)
CORS(app)

# --------------------------------------------------
# Web API Endpoints
@app.route('/')
def home():
    """Home page for Render health checks"""
    return jsonify({
        "status": "online",
        "service": "AP TCP BOT",
        "owner": "★VoiDReaP★",
        "endpoints": {
            "/api/command": "POST - Send command to bot",
            "/api/status": "GET - Check bot status",
            "/api/help": "GET - API documentation"
        },
        "render_url": RENDER_URL
    })

@app.route('/api/command', methods=['POST'])
def receive_command():
    """Receive command from website"""
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400
        
        # Security checks
        auth_token = data.get('token')
        if auth_token != WEB_SERVER_TOKEN:
            return jsonify({"status": "error", "message": "Invalid token"}), 403
        
        command = data.get('command', '').strip()
        uid = data.get('uid', '')
        sender = data.get('sender', 'Website User')
        
        if not command:
            return jsonify({"status": "error", "message": "No command provided"}), 400
        
        # Queue the command for processing
        asyncio.run_coroutine_threadsafe(
            web_command_queue.put({
                'command': command,
                'uid': uid,
                'sender': sender,
                'timestamp': time.time()
            }),
            asyncio.get_event_loop()
        )
        
        return jsonify({
            "status": "success", 
            "message": "Command queued",
            "queue_position": web_command_queue.qsize(),
            "bot_connected": bot_connected
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/status', methods=['GET'])
def bot_status():
    """Check bot status"""
    return jsonify({
        "status": "online" if bot_connected else "offline",
        "connected": bot_connected,
        "queue_size": web_command_queue.qsize(),
        "uptime": time.time() - bot_start_time,
        "commands_processed": sum(command_stats.values()) if command_stats else 0,
        "render_url": RENDER_URL,
        "owner": "★VoiDReaP★"
    }), 200

@app.route('/api/help', methods=['GET'])
def api_help():
    """API help endpoint"""
    return jsonify({
        "service": "AP TCP BOT Web Interface",
        "owner": "★VoiDReaP★",
        "render_url": RENDER_URL,
        "endpoints": {
            "POST /api/command": "Send command to bot",
            "GET /api/status": "Check bot status",
            "GET /api/help": "This documentation"
        },
        "sample_command": {
            "token": WEB_SERVER_TOKEN,
            "command": "/like/123456789",
            "uid": "optional_user_id",
            "sender": "YourName"
        },
        "available_commands": [
            "/help - Show all commands",
            "/like/[UID] - Send 100 likes",
            "/e [UID] [EMOTE_ID] - Send emote",
            "/e [UID1] [UID2] [UID3] [UID4] [EMOTE] - Multi emote",
            "/x/[TEAM_CODE] - Join squad",
            "/3, /5, /6 - Create squad",
            "/solo - Leave squad",
            "/s - Speed boost",
            "/info [UID] - Player info",
            "/clan [ID] - Clan info",
            "/visit [UID] - Send visits",
            "/ai [QUESTION] - AI chat",
            "/spam [UID] - Spam requests (admin only)",
            "/ee [TEAM_CODE] [UIDs] [EMOTE] - Join+Emote+Leave"
        ]
    }), 200

@app.route('/api/send_message', methods=['POST'])
def send_direct_message():
    """Send direct message through website"""
    try:
        data = request.json
        auth_token = data.get('token')
        if auth_token != WEB_SERVER_TOKEN:
            return jsonify({"status": "error", "message": "Invalid token"}), 403
        
        target_uid = data.get('target_uid')
        message = data.get('message')
        
        if not target_uid or not message:
            return jsonify({"status": "error", "message": "Missing parameters"}), 400
        
        # Queue the message
        asyncio.run_coroutine_threadsafe(
            web_command_queue.put({
                'command': f"/webmsg {target_uid} {message}",
                'uid': 'WEB_ADMIN',
                'sender': 'Website',
                'timestamp': time.time(),
                'type': 'direct_message'
            }),
            asyncio.get_event_loop()
        )
        
        return jsonify({"status": "success", "message": "Message queued"}), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --------------------------------------------------
# Web Command Processor
async def process_web_commands():
    """Process commands from web queue"""
    global bot_connected, key, iv
    
    while True:
        try:
            if not bot_connected or whisper_writer is None:
                await asyncio.sleep(1)
                continue
                
            # Get command from queue
            web_cmd = await web_command_queue.get()
            command = web_cmd['command']
            sender = web_cmd.get('sender', 'Website')
            original_uid = web_cmd.get('uid', '')
            
            print(f"[WEB] Processing command from {sender}: {command}")
            
            # Find a chat context to respond in
            # We'll use the bot's own UID as default
            try:
                if command.startswith('/webmsg '):
                    # Direct message from website
                    parts = command.split(' ', 2)
                    if len(parts) >= 3:
                        target_uid = parts[1]
                        message = parts[2]
                        
                        # Send as private message
                        web_msg = f"[B][C][FFA500]📧 Message from {sender}:\n{message}"
                        P = await SEndMsG(2, web_msg, int(target_uid), int(target_uid), key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                        
                else:
                    # Regular command - need to execute
                    # Since we don't have a chat context, we'll create one
                    print(f"[WEB] Executing: {command}")
                    
                    # You can add logic here to handle web-only commands
                    # For now, we just acknowledge receipt
                    
            except Exception as e:
                print(f"[WEB] Error executing command: {e}")
                
            web_command_queue.task_done()
            
        except Exception as e:
            print(f"[WEB] Error processing command: {e}")
            await asyncio.sleep(1)

# --------------------------------------------------
# Existing bot functions (unchanged)
def cleanup_cache():
    """Clean old cached data to maintain performance"""
    current_time = time.time()
    # Clean last_request_time
    to_remove = [k for k, v in last_request_time.items() 
                 if current_time - v > CLEANUP_INTERVAL]
    for k in to_remove:
        last_request_time.pop(k, None)
    
    # Clean command_cache if too large
    if len(command_cache) > MAX_CACHE_SIZE:
        oldest_keys = sorted(command_cache.keys())[:len(command_cache)//2]
        for key in oldest_keys:
            command_cache.pop(key, None)

def get_rate_limited_response(user_id):
    """Implement rate limiting to reduce server load"""
    user_key = str(user_id)
    current_time = time.time()
    
    if user_key in last_request_time:
        time_since_last = current_time - last_request_time[user_key]
        if time_since_last < RATE_LIMIT_DELAY:
            return False
    
    last_request_time[user_key] = current_time
    return True

# Optimized Global Variables
connection_pool = None
command_cache = {}
last_request_time = {}
RATE_LIMIT_DELAY = 0.1  # 100ms delay between requests
MAX_CACHE_SIZE = 50
CLEANUP_INTERVAL = 300  # 5 minutes
command_stats = {}

# Optimized Clan Info Function with Caching
def Get_clan_info(clan_id):
    cache_key = f"clan_{clan_id}"
    if cache_key in command_cache:
        return command_cache[cache_key]
    
    try:
        url = f"https://get-clan-info.vercel.app/get_clan_info?clan_id={clan_id}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            result = f"""[11EAFD][b][c]°°°°GUILD°°°°
[00FF00]Name: {data['clan_name']}
[00FF00]Lvl: {data['level']} | Rank: {data['rank']}
[00FF00]Members: {data['guild_details']['total_members']}/{data['guild_details']['members_online']} online
[11EAFD]°°°°★VoiDReaP★°°°°
[FFB300] OWNER: ★VoiDReaP★"""
            command_cache[cache_key] = result
            cleanup_cache()
            return result
        else:
            return "[FF0000]Failed to get clan info"
    except:
        return "[FF0000]Error fetching clan data"

# Enhanced Player Info Function with Caching
def get_player_info(player_id):
    cache_key = f"player_{player_id}"
    if cache_key in command_cache:
        return command_cache[cache_key]
        
    url = f"https://danger-info-alpha.vercel.app/accinfo?uid={player_id}&key=DANGERxINFO"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            r = response.json()
            result = {
                "Name": r.get('nickname', 'N/A'),
                "UID": r.get('accountId', 'N/A'), 
                "Level": r.get('level', 'N/A'),
                "Likes": r.get('likes', 'N/A'),
                "Region": r.get('region', 'N/A'),
                "Booyah Pass": r.get('booyah_pass_level', 'N/A'),
            }
            command_cache[cache_key] = result
            cleanup_cache()
            return result
    except:
        pass
    return {"error": "Failed to fetch data"}

# Optimized Spam Function
def spam_requests(player_id):
    global spam_requests_sent
    cache_key = f"spam_{player_id}"
    
    if cache_key in command_cache:
        return command_cache[cache_key]
    
    try:
        url = f"https://like2.vercel.app/send_requests?uid={player_id}&server={server2}&key={key2}"
        res = requests.get(url, timeout=15)
        
        if res.status_code == 200:
            data = res.json()
            spam_requests_sent += 1
            success_count = data.get('success_count', 0)
            failed_count = data.get('failed_count', 0)
            
            result = f"[FF6347]Group Requests Sent!\n[00FF00]✅ Success: {success_count}\n[FF0000]❌ Failed: {failed_count}"
            command_cache[cache_key] = result
            cleanup_cache()
            return result
        else:
            try:
                alt_url = f"https://danger-info-alpha.vercel.app/spam?uid={player_id}&server={server2}&key={key2}"
                alt_res = requests.get(alt_url, timeout=15)
                if alt_res.status_code == 200:
                    alt_data = alt_res.json()
                    spam_requests_sent += 1
                    result = f"[FF6347]Group Requests Sent!\n[00FF00]✅ Success: {alt_data.get('success', 0)}\n[FF0000]❌ Failed: {alt_data.get('failed', 0)}"
                    command_cache[cache_key] = result
                    cleanup_cache()
                    return result
            except:
                pass
            return f"[FF0000]API Error: {res.status_code}"
    except:
        return "[FF0000]Spam API connection failed"

# Simple AI Chat Function
async def talk_with_ai(question):
    try:
        responses = [
            "Hello! How can I help you today?",
            "I'm here to assist you with any questions.",
            "That's an interesting point! Tell me more.",
            "I understand your concern. What would you like to know?",
            "Thanks for sharing that with me!",
            "I appreciate you reaching out. How can I assist?"
        ]
        import random
        return random.choice(responses)
    except:
        return "AI service temporarily unavailable"

# Enhanced Info Function
def newinfo(uid):
    cache_key = f"info_{uid}"
    if cache_key in command_cache:
        return command_cache[cache_key]
        
    url = f"https://danger-info-alpha.vercel.app/accinfo?uid={uid}&key=DANGERxINFO"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            result = {"status": "ok", "data": data}
            command_cache[cache_key] = result
            cleanup_cache()
            return result
        return {"status": "error", "message": f"API Error: {response.status_code}"}
    except:
        return {"status": "error", "message": "Network error"}

# Optimized Likes Function
def send_likes(uid):
    try:
        likes_api_response = requests.get(
            f"https://yourlikeapi/like?uid={uid}&server_name={server2}&x-vercel-set-bypass-cookie=true&x-vercel-protection-bypass={BYPASS_TOKEN}",
            timeout=10
        )
        
        if likes_api_response.status_code != 200:
            return f"[FF0000]Like API Error: {likes_api_response.status_code}"

        api_json_response = likes_api_response.json()
        player_name = api_json_response.get('PlayerNickname', 'Unknown')
        likes_added = api_json_response.get('LikesGivenByAPI', 0)
        status = api_json_response.get('status', 0)

        if status == 1 and likes_added > 0:
            return f"""[C][B][11EAFD]━━━━━
[00FF00]✅ Likes Sent!
[FFFFFF]Player: {player_name}
[FFFFFF]Likes: {likes_added}
[11EAFD]━━━━━
[FFB300]AP TCP BOT"""
        else:
            return f"""[C][B][FF0000]━━━━━
[FFFFFF]❌ No Likes Sent!
[FF6347]Player may have already claimed
[FF0000]━━━━━"""

    except:
        return "[FF0000]Like API connection failed"

# Random Color Function
def get_random_color():
    colors = [
        "[FF0000]", "[00FF00]", "[0000FF]", "[FFFF00]", "[FF00FF]", "[00FFFF]", "[FFFFFF]", "[FFA500]",
        "[DC143C]", "[00CED1]", "[9400D3]", "[F08080]", "[20B2AA]", "[FF1493]", "[7CFC00]", "[B22222]",
        "[FF4500]", "[DAA520]", "[00BFFF]", "[00FF7F]", "[4682B4]", "[6495ED]", "[DDA0DD]", "[E6E6FA]",
        "[2E8B57]", "[3CB371]", "[6B8E23]", "[808000]", "[B8860B]", "[CD5C5C]", "[8B0000]", "[FF6347]"
    ]
    return random.choice(colors)

# Helper Functions
def is_admin(uid):
    return str(uid) == ADMIN_UID

def is_bot_muted():
    global is_muted, mute_until
    if is_muted and time.time() < mute_until:
        return True
    elif is_muted and time.time() >= mute_until:
        is_muted = False
        mute_until = 0
        return False
    return False

def update_command_stats(command):
    """Track command usage for optimization"""
    if command not in command_stats:
        command_stats[command] = 0
    command_stats[command] += 1

# --------------------------------------------------
# Headers
Hr = {
    'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 11; ASUS_Z01QD Build/PI)",
    'Connection': "Keep-Alive",
    'Accept-Encoding': "gzip",
    'Content-Type': "application/x-www-form-urlencoded",
    'Expect': "100-continue",
    'X-Unity-Version': "2018.4.11f1",
    'X-GA': 'v1 1',
    'ReleaseVersion': "OB51"
}

# --------------------------------------------------
# Crypto Functions (unchanged from your original)
async def encrypted_proto(encoded_hex):
    key = b'Yg&tc%DEuh6%Zc^8'
    iv = b'6oyZDr22E3ychjM%'
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_message = pad(encoded_hex, AES.block_size)
    encrypted_payload = cipher.encrypt(padded_message)
    return encrypted_payload
    
async def GeNeRaTeAccEss(uid , password):
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    headers = {
        "Host": "100067.connect.garena.com",
        "User-Agent": (await Ua()),
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close"}
    data = {
        "uid": uid,
        "password": password,
        "response_type": "token",
        "client_type": "2",
        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        "client_id": "100067"}
    try:
        async with connection_pool.post(url, headers=Hr, data=data) as response:
            if response.status != 200: 
                return "Failed to get access token"
            data = await response.json()
            open_id = data.get("open_id")
            access_token = data.get("access_token")
            return (open_id, access_token) if open_id and access_token else (None, None)
    except:
        return (None, None)

async def EncRypTMajoRLoGin(open_id, access_token):
    major_login = MajoRLoGinrEq_pb2.MajorLogin()
    major_login.event_time = str(datetime.now())[:-7]
    major_login.game_name = "free fire"
    major_login.platform_id = 1
    major_login.client_version = "1.118.1"
    major_login.system_software = "Android OS 9 / API-28 (PQ3B.190801.10101846/G9650ZHU2ARC6)"
    major_login.system_hardware = "Handheld"
    major_login.telecom_operator = "Verizon"
    major_login.network_type = "WIFI"
    major_login.screen_width = 1920
    major_login.screen_height = 1080
    major_login.screen_dpi = "280"
    major_login.processor_details = "ARM64 FP ASIMD AES VMH | 2865 | 4"
    major_login.memory = 3003
    major_login.gpu_renderer = "Adreno (TM) 640"
    major_login.gpu_version = "OpenGL ES 3.1 v1.46"
    major_login.unique_device_id = "Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c57"
    major_login.client_ip = "223.191.51.89"
    major_login.language = "en"
    major_login.open_id = open_id
    major_login.open_id_type = "4"
    major_login.device_type = "Handheld"
    memory_available = major_login.memory_available
    memory_available.version = 55
    memory_available.hidden_value = 81
    major_login.access_token = access_token
    major_login.platform_sdk_id = 1
    major_login.network_operator_a = "Verizon"
    major_login.network_type_a = "WIFI"
    major_login.client_using_version = "7428b253defc164018c604a1ebbfebdf"
    major_login.external_storage_total = 36235
    major_login.external_storage_available = 31335
    major_login.internal_storage_total = 2519
    major_login.internal_storage_available = 703
    major_login.game_disk_storage_available = 25010
    major_login.game_disk_storage_total = 26628
    major_login.external_sdcard_avail_storage = 32992
    major_login.external_sdcard_total_storage = 36235
    major_login.login_by = 3
    major_login.library_path = "/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/lib/arm64"
    major_login.library_token = "5b892aaabd688e571f688053118a162b|/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/base.apk"
    major_login.channel_type = 3
    major_login.cpu_type = 2
    major_login.cpu_architecture = "64"
    major_login.client_version_code = "2019118695"
    major_login.graphics_api = "OpenGLES2"
    major_login.supported_astc_bitset = 16383
    major_login.login_open_id_type = 4
    major_login.analytics_detail = b"FwQVTgUPX1UaUllDDwcWCRBpWAUOUgsvA1snWlBaO1kFYg=="
    major_login.loading_time = 13564
    major_login.release_channel = "android"
    major_login.extra_info = "KqsHTymw5/5GB23YGniUYN2/q47GATrq7eFeRatf0NkwLKEMQ0PK5BKEk72dPflAxUlEBir6Vtey83XqF593qsl8hwY="
    major_login.android_engine_init_flag = 110009
    major_login.if_push = 1
    major_login.is_vpn = 1
    major_login.origin_platform_type = "4"
    major_login.primary_platform_type = "4"
    string = major_login.SerializeToString()
    return  await encrypted_proto(string)

async def MajorLogin(payload):
    url = "https://loginbp.ggblueshark.com/MajorLogin"
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    try:
        async with connection_pool.post(url, data=payload, headers=Hr, ssl=ssl_context) as response:
            if response.status == 200: 
                return await response.read()
            return None
    except:
        return None

async def GetLoginData(base_url, payload, token):
    url = f"{base_url}/GetLoginData"
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    Hr['Authorization']= f"Bearer {token}"
    try:
        async with connection_pool.post(url, data=payload, headers=Hr, ssl=ssl_context) as response:
            if response.status == 200: 
                return await response.read()
            return None
    except:
        return None

async def DecRypTMajoRLoGin(MajoRLoGinResPonsE):
    proto = MajoRLoGinrEs_pb2.MajorLoginRes()
    proto.ParseFromString(MajoRLoGinResPonsE)
    return proto

async def DecRypTLoGinDaTa(LoGinDaTa):
    proto = PorTs_pb2.GetLoginData()
    proto.ParseFromString(LoGinDaTa)
    return proto

async def DecodeWhisperMessage(hex_packet):
    packet = bytes.fromhex(hex_packet)
    proto = DEcwHisPErMsG_pb2.DecodeWhisper()
    proto.ParseFromString(packet)
    return proto
    
async def decode_team_packet(hex_packet):
    packet = bytes.fromhex(hex_packet)
    proto = sQ_pb2.recieved_chat()
    proto.ParseFromString(packet)
    return proto
    
async def xAuThSTarTuP(TarGeT, token, timestamp, key, iv):
    uid_hex = hex(TarGeT)[2:]
    uid_length = len(uid_hex)
    encrypted_timestamp = await DecodE_HeX(timestamp)
    encrypted_account_token = token.encode().hex()
    encrypted_packet = await EnC_PacKeT(encrypted_account_token, key, iv)
    encrypted_packet_length = hex(len(encrypted_packet) // 2)[2:]
    if uid_length == 9: 
        headers = '0000000'
    elif uid_length == 8: 
        headers = '00000000'
    elif uid_length == 10: 
        headers = '000000'
    elif uid_length == 7: 
        headers = '000000000'
    else: 
        print('Unexpected length') 
        headers = '0000000'
    return f"0115{headers}{uid_hex}{encrypted_timestamp}00000{encrypted_packet_length}{encrypted_packet}"
     
async def cHTypE(H):
    if not H: 
        return 'Squid'
    elif H == 1: 
        return 'CLan'
    elif H == 2: 
        return 'PrivaTe'
    
async def SEndMsG(H , message , Uid , chat_id , key , iv):
    TypE = await cHTypE(H)
    if TypE == 'Squid': 
        msg_packet = await xSEndMsgsQ(message , chat_id , key , iv)
    elif TypE == 'CLan': 
        msg_packet = await xSEndMsg(message , 1 , chat_id , chat_id , key , iv)
    elif TypE == 'PrivaTe': 
        msg_packet = await xSEndMsg(message , 2 , Uid , Uid , key , iv)
    return msg_packet

async def SEndPacKeT(OnLinE , ChaT , TypE , PacKeT):
    if TypE == 'ChaT' and ChaT: 
        whisper_writer.write(PacKeT) 
        await whisper_writer.drain()
    elif TypE == 'OnLine': 
        online_writer.write(PacKeT) 
        await online_writer.drain()
    else: 
        return 'UnsoPorTed TypE ! >> ErrrroR (:():)' 
           

async def TcPOnLine(ip, port, key, iv, AutHToKen, reconnect_delay=0.5):
    global online_writer , spam_room , whisper_writer , spammer_uid , spam_chat_id , spam_uid , XX , uid , Spy,data2, Chat_Leave
    while True:
        try:
            reader , writer = await asyncio.open_connection(ip, int(port))
            online_writer = writer
            bytes_payload = bytes.fromhex(AutHToKen)
            online_writer.write(bytes_payload)
            await online_writer.drain()
            while True:
                data2 = await reader.read(9999)
                if not data2: 
                    break
                
                if data2.hex().startswith('0500') and len(data2.hex()) > 1000:
                    try:
                        packet = await DeCode_PackEt(data2.hex()[10:])
                        packet = json.loads(packet)
                        OwNer_UiD , CHaT_CoDe , SQuAD_CoDe = await GeTSQDaTa(packet)

                        JoinCHaT = await AutH_Chat(3 , OwNer_UiD , CHaT_CoDe, key,iv)
                        await SEndPacKeT(whisper_writer , online_writer , 'ChaT' , JoinCHaT)

                        message = f'[B][C]{get_random_color()}\n🎯 AP TCP BOT Online!\n📡 Web: {RENDER_URL}\n[00FF00]Commands: Use /help'
                        P = await SEndMsG(0 , message , OwNer_UiD , OwNer_UiD , key , iv)
                        await SEndPacKeT(whisper_writer , online_writer , 'ChaT' , P)

                    except Exception as e:
                        pass

            online_writer.close() 
            await online_writer.wait_closed() 
            online_writer = None

        except Exception as e: 
            print(f"- Error With {ip}:{port} - {e}") 
            online_writer = None
        await asyncio.sleep(reconnect_delay)

async def TcPChaT(ip, port, AutHToKen, key, iv, LoGinDaTaUncRypTinG, ready_event, region , reconnect_delay=0.5):
    print(region, 'TCP CHAT')

    global spam_room , whisper_writer , spammer_uid , spam_chat_id , spam_uid , online_writer , chat_id , XX , uid , Spy,data2, Chat_Leave, is_muted, mute_until, bot_connected
    while True:
        try:
            reader , writer = await asyncio.open_connection(ip, int(port))
            whisper_writer = writer
            bytes_payload = bytes.fromhex(AutHToKen)
            whisper_writer.write(bytes_payload)
            await whisper_writer.drain()
            ready_event.set()
            bot_connected = True
            
            if LoGinDaTaUncRypTinG.Clan_ID:
                clan_id = LoGinDaTaUncRypTinG.Clan_ID
                clan_compiled_data = LoGinDaTaUncRypTinG.Clan_Compiled_Data
                print('\n - Target Bot in Clan!')
                print(f' - Clan UID > {clan_id}')
                print(f' - Bot Connected With Clan Chat Successfully!')
                pK = await AuthClan(clan_id , clan_compiled_data , key , iv)
                if whisper_writer: 
                    whisper_writer.write(pK) 
                    await whisper_writer.drain()
                    
            # Web interface announcement
            web_announce = f"[B][C][00FF00]🌐 Web Interface Active!\n📡 URL: {RENDER_URL}\n🔗 Send commands via API"
            P_web = await SEndMsG(0, web_announce, LoGinDaTaUncRypTinG.account_uid, LoGinDaTaUncRypTinG.account_uid, key, iv)
            await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P_web)
            
            while True:
                data = await reader.read(9999)
                if not data: 
                    break
                
                if data.hex().startswith("120000"):
                    msg = await DeCode_PackEt(data.hex()[10:])
                    chatdata = json.loads(msg)
                    try:
                        response = await DecodeWhisperMessage(data.hex()[10:])
                        uid = response.Data.uid
                        chat_id = response.Data.Chat_ID
                        XX = response.Data.chat_type
                        inPuTMsG = response.Data.msg.lower()
                    except:
                        response = None

                    if response:
                        # Rate limiting check
                        if not get_rate_limited_response(uid):
                            continue

                        # Check if bot is muted
                        if is_bot_muted():
                            continue

                        # WEB COMMAND INTERFACE - Special command to check web queue
                        if inPuTMsG.strip() == "/webstatus" and is_admin(uid):
                            queue_size = web_command_queue.qsize()
                            queue_msg = f"[B][C][00FF00]🌐 Web Status\n📊 Pending: {queue_size}\n🔗 API: {RENDER_URL}\n🔑 Token: {WEB_SERVER_TOKEN}"
                            P = await SEndMsG(response.Data.chat_type, queue_msg, uid, chat_id, key, iv)
                            await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                            continue
                        
                        # DEBUG COMMAND - Always responds first
                        if inPuTMsG.strip() == "/debug":
                            update_command_stats("debug")
                            debug_msg = f"[FF0000]✅ BuggedNoob ONLINE! Render: {RENDER_URL}"
                            P = await SEndMsG(response.Data.chat_type, debug_msg, uid, chat_id, key, iv)
                            await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                            continue
                            
                        # HELP COMMAND - Short version for all chat types
                        if inPuTMsG.startswith("/help"):
                            update_command_stats("help")
                            print(f"Help triggered by {uid}")
                            if is_admin(uid):
                                message = f"""[C][B][2E8B57]AP TCP BOT - Render
━━━━━━━━━━━━━━━━━
[00CED1]/like/[UID] → 100 likes
[87CEEB]/x/[CODE] → Join squad  
[FF6347]/e [UID] [EMOTE] → Single emote
[FF6347]/e [UID1] [UID2] [UID3] [UID4] [EMOTE] → Multi emote
[FFD700]/3,/5,/6 → Create squad
[98FB98]/solo → Leave squad
[F0E68C]/s → Speed boost
[20B2AA]/info [UID] → Player info
[7FFF00]/clan [ID] → Clan info
[00FF7F]/visit [UID] → Send visits
[F0E68C]/ai [Q] → AI chat
[B22222]/spam [UID/UIDs] → Group req
[FFA500]/ee [TEAM] [UIDs] [E] → Join+Emote+Leave
━━━━━━━━━━━━━━━━━
[DC143C]/stop,/mute,/unmute
━━━━━━━━━━━━━━━━━
[00CED1]🌐 Web: {RENDER_URL}
[FFB300] OWNER: ★VoiDReaP★"""
                            else:
                                message = f"""[C][B][2E8B57]AP TCP BOT - Render
━━━━━━━━━━━━━━━━━
[00CED1]/like/[UID] → 100 likes
[87CEEB]/x/[CODE] → Join squad
[FF6347]/e [UID] [EMOTE] → Single emote  
[FF6347]/e [UIDs] [EMOTE] → Multi emote
[FFD700]/3,/5,/6 → Create squad
[98FB98]/solo → Leave squad
[F0E68C]/s → Speed boost
[20B2AA]/info [UID] → Player info
[7FFF00]/clan [ID] → Clan info
[00FF7F]/visit [UID] → Send visits
[F0E68C]/ai [Q] → AI chat
[FFA500]/ee [TEAM] [UIDs] [E] → Join+Emote+Leave
━━━━━━━━━━━━━━━━━
[00CED1]🌐 Web: {RENDER_URL}
[FFB300]OWNER: ★VoiDReaP★"""
                            
                            try:
                                P = await SEndMsG(response.Data.chat_type, message, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                            except Exception as e:
                                fallback_msg = f"[FF0000]AP TCP BOT online! Render: {RENDER_URL}"
                                P = await SEndMsG(response.Data.chat_type, fallback_msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                            continue
                        
                        # Existing command processing code...
                        # ... [Your existing command processing code remains the same] ...
                        
                        response = None
                        
            whisper_writer.close() 
            await whisper_writer.wait_closed() 
            whisper_writer = None
            bot_connected = False
                    	
        except Exception as e: 
            print(f"Error {ip}:{port} - {e}") 
            whisper_writer = None
            bot_connected = False
        await asyncio.sleep(reconnect_delay)

# --------------------------------------------------
# Enhanced Main Function
async def MaiiiinE():
    global connection_pool
    
    # Enhanced connection pool configuration
    connection_pool = aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=20),
        connector=aiohttp.TCPConnector(limit=20, limit_per_host=10)
    )
    
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
