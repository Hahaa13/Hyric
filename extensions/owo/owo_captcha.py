import re
import discord
from discord.ext import commands
from utils.bot import Bot

class OwO_Captcha(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.owo = self.bot.get_cog("OwO")
        self.owo_user = self.bot.get_user(self.owo.configs["owo_id"])
        self.dm_channel = self.owo_user.dm_channel

    async def cog_load(self):
        if self.dm_channel is None:
            self.dm_channel = await self.owo_user.create_dm()

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.owo_user.id == message.author.id:
            if "https://owobot.com/captcha" in message.content and (isinstance(message.channel, discord.channel.DMChannel) or self.bot.user.display_name in message.content or self.bot.user.name in message.content or str(self.bot.user.id) in message.content):
                self.owo.captcha = True
            elif "⚠️" in message.content and (isinstance(message.channel, discord.channel.DMChannel) or self.bot.user.display_name in message.content or self.bot.user.name in message.content or str(self.bot.user.id) in message.content):
                self.owo.captcha = True
                if len(message.attachments) > 0:
                    captcha_url = message.attachments[0].url
                    length = int(re.findall("[0-9] letter", message.content)[0].replace(" letter", ""))
                    def check(m) -> bool:
                        return m.author.id == self.owo_user.id and isinstance(m.channel, discord.channel.DMChannel)
                    for _ in range(self.owo.configs["max_captcha_attemp"]):
                        captcha = self.bot.solver.normal(captcha_url, maxlen=length, minlen=length, numeric=4, case=True)
                        await self.dm_channel.send(captcha["code"])
                        message = await self.bot.wait_for("message", check=check, timeout=10)
                        if "🚫" in message.content:
                            self.bot.solver.report(captcha["id"], False)
                            self.bot.logger.warning("CAPTCHA - ERROR")
                            continue
                        self.bot.solver.report(captcha["id"], True)
                        self.bot.logger.info(f"CAPTCHA - SLOVED CODE: {captcha['code']}")
                        self.owo.captcha = False
                        return
                else:
                    self.bot.logger.info("CAPTCHA - NOT FOUND")
                    
async def setup(bot: Bot) -> None:
    if bot.configs["2captcha"] != "":
        await bot.add_cog(OwO_Captcha(bot))