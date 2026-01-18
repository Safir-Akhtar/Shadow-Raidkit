# backend.py - Shadow Tools LuciferAi Beast Backend (FINAL FIXED 2026)
# Run in venv: python backend.py

import asyncio
import threading
import time
import webbrowser
from http.server import SimpleHTTPRequestHandler, HTTPServer
import socketserver
import pyaudio
import discord
from discord.ext import commands
import websockets
import json
import random

# ─── CONFIG ────────────────────────────────────────────────
PORT_HTTP = 8000
PORT_WS = 6666

TOKENS = []                    # frontend se load honge
CLIENTS = {}                   # token → bot
VOICE_CLIENTS = {}             # token → voice client

MIC_BROADCAST_ACTIVE = False
MIC_DEVICE_INDEX = None
JOIN_ACTIVE = False
CURRENT_GUILD_ID = None
CURRENT_VC_CHANNEL_ID = None

CONNECTED_WS = set()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

# ─── Discord Selfbot ───────────────────────────────────────
class LuciferBot(commands.Bot):
    def __init__(self, token):
        super().__init__(command_prefix="l!", intents=intents, self_bot=True)
        self.token = token

    async def setup_hook(self):
        print(f"[Shadow Tools] Logged in as {self.user} ({self.user.id})")
        broadcast({"type": "log", "msg": f"Alt online: {self.user} ({self.user.id})", "level": "success"})

# ─── WebSocket Server ──────────────────────────────────────
async def ws_handler(websocket):
    CONNECTED_WS.add(websocket)
    print(f"[WS] Frontend connected - total: {len(CONNECTED_WS)}")
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                await handle_command(data)
            except json.JSONDecodeError:
                print("[WS] Invalid JSON")
    except:
        pass
    finally:
        CONNECTED_WS.remove(websocket)

def broadcast(data):
    payload = json.dumps(data)
    for ws in list(CONNECTED_WS):
        try:
            asyncio.create_task(ws.send(payload))
        except:
            CONNECTED_WS.remove(ws)

async def handle_command(data):
    cmd = data.get("type")

    if cmd == "load_tokens":
        new_tokens = data.get("tokens", [])
        loaded = 0
        for tok in new_tokens:
            if tok not in CLIENTS:
                bot = LuciferBot(tok)
                CLIENTS[tok] = bot
                asyncio.create_task(bot.start(tok, bot=True, reconnect=True))
                loaded += 1
        broadcast({"type": "log", "msg": f"Loaded {loaded} alts", "level": "success"})
        broadcast({"type": "tokens_update", "count": len(CLIENTS)})

    elif cmd == "vc_join_toggle":
        global JOIN_ACTIVE, CURRENT_GUILD_ID, CURRENT_VC_CHANNEL_ID
        JOIN_ACTIVE = data.get("active", False)
        CURRENT_GUILD_ID = data.get("guild_id")
        CURRENT_VC_CHANNEL_ID = data.get("channel_id")
        if JOIN_ACTIVE and CURRENT_VC_CHANNEL_ID:
            joined = 0
            for bot in CLIENTS.values():
                channel = bot.get_channel(int(CURRENT_VC_CHANNEL_ID))
                if channel and isinstance(channel, discord.VoiceChannel):
                    try:
                        vc = await channel.connect(reconnect=True)
                        VOICE_CLIENTS[bot.token] = vc
                        joined += 1
                    except Exception as e:
                        broadcast({"type": "log", "msg": f"VC join fail: {e}", "level": "error"})
            broadcast({"type": "vc_status", "connected": True, "joined": joined})
        else:
            for vc in VOICE_CLIENTS.values():
                if vc: await vc.disconnect(force=True)
            VOICE_CLIENTS.clear()
            broadcast({"type": "vc_status", "connected": False})

    elif cmd == "mic_toggle":
        global MIC_BROADCAST_ACTIVE, MIC_DEVICE_INDEX
        MIC_BROADCAST_ACTIVE = data.get("active", False)
        MIC_DEVICE_INDEX = data.get("device_index")
        broadcast({"type": "log", "msg": f"Mic {'ON' if MIC_BROADCAST_ACTIVE else 'OFF'} (device {MIC_DEVICE_INDEX})", "level": "warn"})
        broadcast({"type": "mic_status", "active": MIC_BROADCAST_ACTIVE})

    elif cmd == "kill_all":
        count = len(CLIENTS)
        for bot in CLIENTS.values():
            await bot.close()
        CLIENTS.clear()
        VOICE_CLIENTS.clear()
        MIC_BROADCAST_ACTIVE = False
        JOIN_ACTIVE = False
        broadcast({"type": "log", "msg": f"KILL SWITCH - {count} alts dead", "level": "error"})

# ─── Mic Broadcast Thread ──────────────────────────────────
def mic_thread():
    p = pyaudio.PyAudio()
    stream = None
    try:
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=48000, input=True, frames_per_buffer=960, input_device_index=MIC_DEVICE_INDEX)
        while True:
            if not MIC_BROADCAST_ACTIVE:
                time.sleep(0.05)
                continue
            try:
                data = stream.read(960, exception_on_overflow=False)
                for vc in VOICE_CLIENTS.values():
                    if vc and vc.is_connected():
                        vc.send_audio_packet(data, encode=True)
            except:
                time.sleep(0.5)
    except Exception as e:
        print(f"[Mic] Error: {e}")
    finally:
        if stream: stream.close()
        p.terminate()

# ─── Local HTTP Server ─────────────────────────────────────
class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=".", **kwargs)

def start_http():
    with socketserver.TCPServer(("", PORT_HTTP), Handler) as httpd:
        print(f"[Lucifer] GUI serving at http://localhost:{PORT_HTTP}")
        time.sleep(2)  # 2 sec wait
        webbrowser.open(f"http://localhost:{PORT_HTTP}")
        httpd.serve_forever()

# ─── Main ──────────────────────────────────────────────────
async def main():
    print("SHADOW TOOLS")
    print("[LuciferAi] Beast awakening...")
    threading.Thread(target=start_http, daemon=True).start()
    threading.Thread(target=mic_thread, daemon=True).start()

    async with websockets.serve(ws_handler, "localhost", PORT_WS):
        print(f"[Lucifer] WebSocket server running on ws://localhost:{PORT_WS}")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())