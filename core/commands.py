# core/commands.py - Shadow Tools frontend se aane wale commands ka handler
import asyncio
from .config import (
    TOKENS, CLIENTS, VOICE_CLIENTS,
    MIC_BROADCAST_ACTIVE, MIC_DEVICE_INDEX, JOIN_ACTIVE,
    CURRENT_GUILD_ID, CURRENT_VC_CHANNEL_ID,
    CONNECTED_WS_CLIENTS
)
from .discord_bot import LuciferBot
from .websocket import broadcast

async def handle_frontend_command(data: dict):
    cmd = data.get("type")
    print(f"[Shadow Command] Received: {cmd} | Data: {data}")

    if cmd == "load_tokens":
        new_tokens = data.get("tokens", [])
        if not new_tokens:
            broadcast({"type": "log", "msg": "No tokens sent from frontend", "level": "error"})
            return

        loaded = 0
        for tok in new_tokens:
            if tok not in CLIENTS:
                bot = LuciferBot(tok)
                CLIENTS[tok] = bot
                asyncio.create_task(bot.start(tok, bot=True, reconnect=True))
                loaded += 1
        broadcast({
            "type": "log",
            "msg": f"Shadow Tools loaded {loaded}/{len(new_tokens)} new alts",
            "level": "success"
        })
        broadcast({
            "type": "tokens_update",
            "count": len(CLIENTS),
            "online": loaded
        })

    elif cmd == "vc_join_toggle":
        global JOIN_ACTIVE, CURRENT_GUILD_ID, CURRENT_VC_CHANNEL_ID
        JOIN_ACTIVE = data.get("active", False)
        CURRENT_GUILD_ID = data.get("guild_id")
        CURRENT_VC_CHANNEL_ID = data.get("channel_id")

        if JOIN_ACTIVE and CURRENT_VC_CHANNEL_ID:
            joined = 0
            for bot in list(CLIENTS.values()):
                try:
                    channel = bot.get_channel(int(CURRENT_VC_CHANNEL_ID))
                    if channel and isinstance(channel, discord.VoiceChannel):
                        vc = await channel.connect(reconnect=True)
                        VOICE_CLIENTS[bot.token] = vc
                        joined += 1
                except Exception as e:
                    broadcast({"type": "log", "msg": f"VC join failed on one alt: {e}", "level": "error"})
            broadcast({
                "type": "vc_status",
                "connected": True,
                "joined_count": joined,
                "guild_id": CURRENT_GUILD_ID,
                "vc_id": CURRENT_VC_CHANNEL_ID,
                "msg": f"Shadow Tools joined VC with {joined} alts"
            })
        else:
            disconnected = len(VOICE_CLIENTS)
            for vc in list(VOICE_CLIENTS.values()):
                if vc:
                    try:
                        await vc.disconnect(force=True)
                    except:
                        pass
            VOICE_CLIENTS.clear()
            broadcast({
                "type": "vc_status",
                "connected": False,
                "disconnected_count": disconnected,
                "msg": "All alts left VC"
            })

    elif cmd == "mic_toggle":
        global MIC_BROADCAST_ACTIVE, MIC_DEVICE_INDEX
        MIC_BROADCAST_ACTIVE = data.get("active", False)
        MIC_DEVICE_INDEX = data.get("device_index")
        status = "ENABLED" if MIC_BROADCAST_ACTIVE else "DISABLED"
        broadcast({
            "type": "log",
            "msg": f"Shadow Tools mic broadcast {status} (device index: {MIC_DEVICE_INDEX})",
            "level": "warn"
        })
        broadcast({
            "type": "mic_status",
            "active": MIC_BROADCAST_ACTIVE,
            "device_index": MIC_DEVICE_INDEX
        })

    elif cmd == "kill_all":
        alt_count = len(CLIENTS)
        for bot in list(CLIENTS.values()):
            try:
                await bot.close()
            except:
                pass
        CLIENTS.clear()
        VOICE_CLIENTS.clear()
        MIC_BROADCAST_ACTIVE = False
        JOIN_ACTIVE = False
        broadcast({
            "type": "log",
            "msg": f"SHADOW KILL SWITCH ACTIVATED - {alt_count} alts terminated",
            "level": "error"
        })
        broadcast({"type": "kill_confirmed", "killed": alt_count})

    else:
        broadcast({
            "type": "log",
            "msg": f"Unknown Shadow command received: {cmd}",
            "level": "error"
        })