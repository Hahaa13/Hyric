import json
from datetime import datetime
from discord.ext import commands
from utils.bot import Bot
from utils.strfdelta import strfdelta

class Commands(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return ctx.author.id in self.bot.configs["user_allow_commands"] or ctx.author.id == self.bot.user.id

    @commands.command()
    async def stop(self, ctx) -> None:
        await self.bot.webhook.send(self.bot.user, "🔴STOP BOT", "⚠️IF YOU USE PTERODACTYL PANEL, THE BOT MAY RESTART AUTOMATICALLY. PLEASE CHECK CAREFULLY")
        await self.bot.close()
        exit()

    @commands.command()
    async def uptime(self, ctx) -> None:
        await self.bot.webhook.send(self.bot.user, "⏰Uptime", f"Current uptime is {strfdelta((datetime.utcnow() - self.bot.time_onload), '%H:%M:%S')}")

async def setup(bot: Bot):
    await bot.add_cog(Commands(bot))