import json
from datetime import datetime
from discord.ext import commands
from utils.bot import *
from utils.strfdelta import strfdelta

class Commands(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def command_stop(self, message) -> None:
        if Command.is_commamd(message, self.bot):
            if "stop" in message.content:
                await self.bot.webhook.send(self.bot.user, "🔴STOP BOT", "⚠️IF YOU USE PTERODACTYL PANEL, THE BOT MAY RESTART AUTOMATICALLY. PLEASE CHECK CAREFULLY")
                await self.bot.close()
                exit()
            elif "uptime" in message.content:
                await self.bot.webhook.send(self.bot.user, "⏰Uptime", f"Current uptime is {strfdelta((datetime.utcnow() - self.bot.time_onload), '%H:%M:%S')}")

async def setup(bot: Bot):
    await bot.add_cog(Commands(bot))