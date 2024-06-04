import random
import asyncio
from discord.ext import commands, tasks
from utils.bot import Bot

class Listener(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def cog_load(self):
        if len(self.bot.configs["channel_ids"]) > 1:
            self.change_channel.start()
        else:
            self.bot.channel = self.bot.get_channel(self.bot.configs["channel_ids"][0])
            self.bot.logger.info(f"SELECT CHANNEL {self.bot.channel.id}")

    @tasks.loop(seconds=3)
    async def change_channel(self):
        for channel_id in self.bot.configs["channel_ids"]:
            if random.randint(0,len(self.bot.configs["channel_ids"])) == 0:
                self.bot.channel = self.bot.get_channel(channel_id)
                if self.bot.channel != None:
                    break
        else:
            self.bot.channel = self.bot.get_channel(self.bot.configs["channel_ids"][0])
        self.bot.logger.info(f"SELECT CHANNEL {self.bot.channel.id}. WILL CHANGE IN {self.bot.configs['change_channel_later']} MINS")
        await asyncio.sleep(self.bot.configs["change_channel_later"]*60, self.bot.configs["change_channel_later"]*60+10)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error) -> None:
        if isinstance(error, commands.CommandNotFound):
            return
        raise error
        
async def setup(bot: Bot):
    await bot.add_cog(Listener(bot))