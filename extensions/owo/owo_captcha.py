import re
import discord
from aiohttp import ClientSession
from discord.ext import commands
from utils.bot import Bot
from utils.oauth import Oauth2
from utils.captcha_handler import *

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
    async def on_message(self, message) -> None:
        if self.owo_user.id == message.author.id or self.bot.user.id == message.author.id:
            if "https://owobot.com/captcha" in message.content and (isinstance(message.channel, discord.channel.DMChannel) or self.bot.user.display_name in message.content or self.bot.user.name in message.content or str(self.bot.user.id) in message.content):
                self.owo.pause = True
                self.owo.captcha = True
                self.bot.logger.warning("CAPTCHA LINK FOUND")
                await self.bot.webhook.send(self.bot.user, "OWO CAPTCHA LINK FOUND", ping=True)
                captcha = HCaptchaSolver(self.bot.configs, self.bot.logger, "a6a1d5ce-612d-472d-8e37-7601408fbc09", "https://owobot.com/captcha")
                headers = {"Accept": "application/json, text/plain, */*","Accept-Encoding": "gzip, deflate, br","Accept-Language": "en-US;en;q=0.8","Content-Type": "application/json;charset=UTF-8","Origin": "https://owobot.com","Referer": "https://owobot.com/captcha",'Sec-Fetch-Dest': 'empty','Sec-Fetch-Mode': 'cors','Sec-Fetch-Site': 'same-origin',"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0"}
                for retry in range(self.owo.configs["max_link_captcha_attemp"]):
                    if not captcha.work:
                        self.bot.logger.warning("CAPTCHA LINK NOT SOLVED")
                        break
                    oauth = Oauth2(self.bot.account["token"], "https://discord.com/oauth2/authorize?response_type=code&redirect_uri=https%3A%2F%2Fowobot.com%2Fapi%2Fauth%2Fdiscord%2Fredirect&scope=identify%20guilds%20email%20guilds.members.read&client_id=408785106942164992", self.bot.logger)
                    async with (await oauth.get_oauth()) as session:
                        cookies = {cookie.key: cookie.value for cookie in session.cookie_jar}
                        async with session.get("https://owobot.com/api/captcha/verify",headers=headers,json={"token": captcha.getresult()},cookies=cookies) as res:
                            self.bot.logger.info(f"SOLVED CAPTCHA LINK - {res.status}")
                            await self.bot.webhook.send(self.bot.user, f"OWO CAPTCHA LINK SOLVED - {res.status}")
                            self.owo.pause = False
                            self.owo.captcha = False
                            break
                else:
                    await self.bot.webhook.send(self.bot.user, "OWO CAPTCHA LINK FAILED TO SOLVE", ping=True)
            elif "⚠️" in message.content and (isinstance(message.channel, discord.channel.DMChannel) or self.bot.user.display_name in message.content or self.bot.user.name in message.content or str(self.bot.user.id) in message.content):
                self.owo.pause = True
                self.owo.captcha = True
                if len(message.attachments) > 0:
                    self.bot.logger.warning("CAPTCHA IMAGE FOUND")
                    await self.bot.webhook.send(self.bot.user, "OWO CAPTCHA IMAGE FOUND", ping=True)
                    length = int(re.findall("[0-9] letter", message.content)[0].replace(" letter", ""))
                    def check(m) -> bool:
                        return m.author.id == self.owo_user.id and isinstance(m.channel, discord.channel.DMChannel)
                    captcha = CaptchaSolverNormal(message.attachments[0].url, self.bot.configs, self.bot.logger)
                    for retry in range(self.owo.configs["max_captcha_attemp"]):
                        captcha.solver(maxlen=length, minlen=length)
                        if not captcha.work:
                            self.bot.logger.warning("CAPTCHA NOT SOLVED")
                            break
                        await self.dm_channel.send(captcha.getresult())
                        messagec = await self.bot.wait_for("message", check=check, timeout=10)
                        if "🚫" in messagec.content:
                            captcha.report(False)
                            self.bot.logger.warning("CAPTCHA FAILED")
                            await self.bot.webhook.send(self.bot.user, "OWO CAPTCHA FAILED")
                            continue
                        captcha.report(True)
                        self.bot.logger.info(f"CAPTCHA - SLOVED CODE: {captcha.getresult()}")
                        await self.bot.webhook.send(self.bot.user, f"OWO CAPTCHA SOLVED CODE: {captcha.getresult()}")
                        self.owo.pause = False
                        self.owo.captcha = False
                        break
                    else:
                        await self.bot.webhook.send(self.bot.user, "OWO CAPTCHA NOT SOLVED", ping=True)
                else:
                    self.bot.logger.info("CAPTCHA - FOUND AND NO IMAGE")
                    return
                    
async def setup(bot: Bot) -> None:
    await bot.add_cog(OwO_Captcha(bot))