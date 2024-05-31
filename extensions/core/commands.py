import sys
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
        await ctx.send("🧨STOP BOT")
        await ctx.send("⚠️If you use Pterodactyl panel, the bot may restart automatically. Please check carefully")
        await self.bot.close()
        sys.exit(1) 

    @commands.command()
    async def uptime(self, ctx) -> None:
        content = f"```⏰Uptime: {strfdelta((datetime.utcnow() - self.bot.time_onload), '%H:%M:%S')}```"
        await ctx.send(content)

async def setup(bot: Bot):
    await bot.add_cog(Commands(bot))