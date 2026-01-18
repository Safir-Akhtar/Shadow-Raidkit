# core/discord_bot.py - Shadow Tools ka core selfbot class
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

class LuciferBot(commands.Bot):
    def __init__(self, token: str):
        super().__init__(
            command_prefix="l!",
            intents=intents,
            self_bot=True,
            help_command=None  # No default help command
        )
        self.token = token

    async def setup_hook(self):
        print(f"[Shadow Tools] Logged in as {self.user} ({self.user.id})")
        from .websocket import broadcast
        broadcast({
            "type": "log",
            "msg": f"Shadow alt online: {self.user} ({self.user.id})",
            "level": "success"
        })

    async def on_error(self, event_method, *args, **kwargs):
        print(f"[Shadow Tools] Error in {event_method}: {args} {kwargs}")
        from .websocket import broadcast
        broadcast({
            "type": "log",
            "msg": f"Error on alt {self.user}: {args}",
            "level": "error"
        })