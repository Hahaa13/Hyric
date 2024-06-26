import json
from discord.ext import commands
from utils.bot import Bot

class Core(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def cog_load(self):
        if self.bot.account["voice_afk"]:
            vc = self.bot.get_channel(self.bot.account["voice_afk"])
            await vc.connect()

async def setup(bot: Bot) -> None:
    await bot.add_cog(Core(bot))