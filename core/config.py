# core/config.py - Shadow Tools ke sab global settings yahan
# Is file ko change karke ports, defaults, etc. set kar sakta hai

PORT_HTTP = 8000               # Frontend GUI serve karega yahan
PORT_WS = 6666                 # WebSocket backend-frontend communication

# Global state (live variables jo runtime mein change honge)
TOKENS = []                    # Loaded tokens list (frontend se aayenge)
CLIENTS = {}                   # token str → LuciferBot object
VOICE_CLIENTS = {}             # token str → discord.VoiceClient object

MIC_BROADCAST_ACTIVE = False   # Mic live broadcast on/off
MIC_DEVICE_INDEX = None        # PyAudio device index (frontend se select)

JOIN_ACTIVE = False            # VC join mode on/off
CURRENT_GUILD_ID = None        # Current target guild/server ID
CURRENT_VC_CHANNEL_ID = None   # Current voice channel ID
CURRENT_TEXT_CHANNELS = []     # List of text channel IDs for spam (future)

CONNECTED_WS_CLIENTS = set()   # Active WebSocket connections from frontend