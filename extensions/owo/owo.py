import re
import discord
import asyncio
import datetime
import aiohttp
import random
import json
from discord.ext import commands, tasks
from utils.bot import Bot
from extensions.owo.utils import *

class OwO(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.captcha = False
        self.lock = asyncio.Lock()
        self.hbcaptcha = HuntBotCaptcha()
        self.configs = json.load(open("extensions/owo/_configs.json"))
        self.caches = json.load(open("extensions/owo/_caches.json"))
        self.gem = Gem(bot, self.configs)
        fuctions = [self.hunt, self.battle, self.daily, self.pray_or_curse, self.sell, self.sac, self.cookie, self.run, self.pup, self.piku, self.huntbot, self.text_exp, self.text_owo]
        enables = ["hunt", "battle", "daily", "pray_or_curse", "sell", "sac", "cookie", "run", "pup", "piku", "huntbot", "text_exp", "text_owo"]
        self.cachemanager.start()
        for fuction, enable in zip(fuctions, enables):
            if self.configs["enables"][enable]:
                fuction.start()

    def getTimeCooldown(self) -> int:
        test = datetime.datetime.utcnow().replace(hour=7,minute=0,second=0,microsecond=0)
        if datetime.datetime.utcnow() < test:
            test = test - datetime.timedelta(days=1)
        return (test - datetime.datetime.utcnow()).seconds

    async def cooldown_command(self) -> None:
        async with self.lock:
            await asyncio.sleep(random.randint(3,5))

    def addCache(self, *keys) -> None:
        with open("extensions/owo/_caches.json", "w") as f:
            if len(keys) < 2: self.caches["checks"][keys[0]] = True
            else: self.caches[keys[0]][keys[1]] = True
            json.dump(self.caches, f)

    @tasks.loop(seconds=3)
    async def cachemanager(self) -> None:
        now = datetime.datetime.utcnow()
        old = datetime.datetime.fromtimestamp(self.caches["time"])
        if (old.hour < 7 or now.day > old.day) or now.month > old.month or now.year > old.year:
            if now.hour >= 7 or now.day - old.day > 2:
                self.bot.logger.info("RESET CACHES")
                self.caches["time"] = now.timestamp()
                for k in self.caches["checks"].keys():
                    self.caches["checks"][k] = False
                with open("extensions/owo/_caches.json", "w") as f:
                    json.dump(self.caches, f, indent=4)
                return
        await asyncio.sleep(self.getTimeCooldown())

    @tasks.loop(seconds=3)
    async def hunt(self) -> None:
        if not self.captcha:
            await self.cooldown_command()
            if not self.gem.ready:
                await self.gem.gem_data_collect(self.bot.channel)
            await self.bot.channel.send(f"{self.configs['owo_prefix']} hunt")
            def check(m) -> bool:
                return m.author.id == self.configs["owo_id"] and m.channel.id == self.bot.channel.id and f"**🌱 | {self.bot.user.display_name}**" in m.content
            message = await self.bot.wait_for('message', check=check, timeout=5)
            await self.gem.on_hunt(message)
            xp = re.findall("[0-9]{1,99}xp", message.content)
            self.bot.logger.info(f"OWO HUNT - {xp[0].upper()}")
            await asyncio.sleep(random.randint(18,25))

    @tasks.loop(seconds=3)
    async def battle(self) -> None:
        if not self.captcha:
            await self.cooldown_command()
            await self.bot.channel.send(f"{self.configs['owo_prefix']} battle")
            self.bot.logger.info("OWO BATTLE")
            await asyncio.sleep(random.randint(18,25))

    @tasks.loop(seconds=3)
    async def daily(self) -> None:
        if not self.captcha:
            if self.caches["checks"]["daily"]:
                await asyncio.sleep(self.getTimeCooldown() + 10)
            await self.cooldown_command()
            await self.bot.channel.send(f"{self.configs['owo_prefix']} daily")
            timesec = self.getTimeCooldown()
            def check(m) -> bool:
                return m.author.id == self.configs["owo_id"] and m.channel.id == self.bot.channel.id and self.bot.user.display_name in m.content
            message = await self.bot.wait_for('message', check=check, timeout=5)
            if f"**⏱ |** Nu! **{self.bot.user.display_name}**!" in message.content:
                self.bot.logger.info(f"DAILY COOLDOWN {timesec}s")
            elif f"💰 **| {self.bot.user.display_name}**, Here is your daily " in message.content:
                self.bot.logger.info(f"DAILY CLAIMED, NEXT DAILY IN {timesec}s")
            self.addCache("daily")
            await asyncio.sleep(timesec)

    @tasks.loop(seconds=3)
    async def pray_or_curse(self):
        if not self.captcha:
            await self.cooldown_command()
            poc_user = ""
            if self.configs["pray_or_curse_id"] > 0:
                poc_user = f"<@{self.configs['pray_or_curse_id']}>"
            await self.bot.channel.send(f"{self.configs['owo_prefix']} {self.configs['enables']['pray_or_curse']} {poc_user}")
            self.bot.logger.info(f"OWO {self.configs['enables']['pray_or_curse'].upper()} {poc_user}")
            await asyncio.sleep(random.randint(310, 360))

    @tasks.loop(seconds=3)
    async def sell(self) -> None:
        if not self.captcha:
            await self.cooldown_command()
            await self.bot.channel.send(f"{self.configs['owo_prefix']} sell {self.configs['enables']['sell']}")
            def check(m) -> bool:
                return m.author.id == self.configs["owo_id"] and m.channel.id == self.bot.channel.id and f"**🔪 | {self.bot.user.display_name}** sold" in m.content
            message = await self.bot.wait_for('message', check=check, timeout=8)
            cow = re.findall(" [0-9]{1,99}", message.content)[0]
            self.bot.logger.info(f"OWO SELL {self.configs['enables']['sell'].upper()} -{cow} COW")
            await asyncio.sleep(random.randint(311, 360))

    @tasks.loop(seconds=3)
    async def sac(self) -> None:
        if not self.captcha:
            await self.cooldown_command()
            await self.bot.channel.send(f"{self.configs['owo_prefix']} sac {self.configs['enables']['sac']}")
            def check(m) -> bool:
                return m.author.id == self.configs["owo_id"] and m.channel.id == self.bot.channel.id and f"**🔪 | {self.bot.user.display_name}** sacrificed" in m.content
            message = await self.bot.wait_for('message', check=check, timeout=8)
            sac = re.findall(" [0-9]{1,99}", message.content)[0]
            self.bot.logger.info(f"OWO SAC {self.configs['enables']['sac'].upper()} -{sac} SACRIFICED")
            await asyncio.sleep(random.randint(312, 360))

    @tasks.loop(seconds=3)
    async def cookie(self) -> None:
        if not self.captcha:
            if self.caches["checks"]["cookie"]:
                await asyncio.sleep(self.getTimeCooldown() + 10)
            await self.cooldown_command()
            await self.bot.channel.send(f"{self.configs['owo_prefix']} cookie <@{self.configs['enables']['cookie']}>")
            self.bot.logger.info(f"OWO COOKIE {self.configs['enables']['cookie']}")
            self.addCache("cookie")
            await asyncio.sleep(self.getTimeCooldown())

    @tasks.loop(seconds=3)
    async def run(self) -> None:
        if not self.captcha:
            if self.caches["checks"]["run"]:
                await asyncio.sleep(self.getTimeCooldown() + 10)
            await self.cooldown_command()
            await self.bot.channel.send(f"{self.configs['owo_prefix']} run")
            def check(m) -> bool:
                return m.author.id == self.configs["owo_id"] and m.channel.id == self.bot.channel.id and "run" in m.content
            message = await self.bot.wait_for('message', check=check, timeout=5)
            if "🚫" in message.content:
                self.bot.logger.info("OWO RUN FULL")
                self.addCache("run")
                timesec = self.getTimeCooldown()
            else:
                self.bot.logger.info("OWO RUN")
                timesec = random.randint(60,80)
            await asyncio.sleep(timesec)

    @tasks.loop(seconds=3)
    async def pup(self) -> None:
        if not self.captcha:
            if self.caches["checks"]["pup"]:
                await asyncio.sleep(self.getTimeCooldown() + 10)
            await self.cooldown_command()
            await self.bot.channel.send(f"{self.configs['owo_prefix']} pup")
            def check(m) -> bool:
                return m.author.id == self.configs["owo_id"] and m.channel.id == self.bot.channel.id and "pup" in m.content
            message = await self.bot.wait_for('message', check=check, timeout=5)
            if "🚫" in message.content:
                self.bot.logger.info("OWO PUP FULL")
                self.addCache("pup")
                timesec = self.getTimeCooldown()
            else:
                self.bot.logger.info("OWO PUP")
                timesec = random.randint(60,80)
            await asyncio.sleep(timesec)

    @tasks.loop(seconds=3)
    async def piku(self) -> None:
        if not self.captcha:
            if self.caches["checks"]["piku"]:
                await asyncio.sleep(self.getTimeCooldown() + 10)
            await self.cooldown_command()
            await self.bot.channel.send(f"{self.configs['owo_prefix']} piku")
            def check(m) -> bool:
                return m.author.id == self.configs["owo_id"] and m.channel.id == self.bot.channel.id and "carrot" in m.content
            message = await self.bot.wait_for('message', check=check, timeout=5)
            if "🚫" in message.content:
                self.bot.logger.info("OWO PIKU FULL")
                self.addCache("piku")
                timesec = self.getTimeCooldown()
            else:
                self.bot.logger.info("OWO PIKU")
                timesec = random.randint(60,80)
            await asyncio.sleep(timesec)

    @tasks.loop(seconds=3)
    async def huntbot(self) -> None:
        if not self.captcha:
            await self.cooldown_command()
            await self.bot.channel.send(f"{self.configs['owo_prefix']} hb {self.configs['enables']['huntbot']}")
            def check(m) -> bool:
                return m.author.id == self.configs["owo_id"] and m.channel.id == self.bot.channel.id
            message = await self.bot.wait_for('message', check=check, timeout=5)
            if "|** `BEEP BOOP. I AM BACK WITH" in message.content:
                self.bot.logger.info("OWO HUNTBOT CLAIMED")
                return
            elif f"**🚫 | {self.bot.user.display_name}**, You don't have enough cowoncy!" in message.content:
                self.bot.logger.info("OWO HUNTBOT NO COWONCY. WAIT 5MINS")
                await asyncio.sleep(300)
                return
            elif "|** `BEEP BOOP. I AM STILL HUNTING" in message.content:
                wait_time = re.findall("[0-9]{0,2}H{0,1} {0,1}[0-9]{1,2}M", message.content)[0]
                wait_sec = int(re.findall("[0-9]{1,2}M",wait_time)[0].replace("M", ""))*60
                if "H" in wait_time:
                    wait_sec += int(re.findall("[0-9]{0,2}H",wait_time)[0].replace("H", ""))*60*60
                self.bot.logger.info(f"OWO HUNTBOT IS RUNNING. WILL BACK IN {wait_time}")
                await asyncio.sleep(wait_sec+60)
                return
            elif f"**🚫 | {self.bot.user.display_name}**, Please include your password!" in message.content:
                async for check_message in message.channel.history(limit=100):
                    if "Cex**, Here is your password!" in check_message.content:
                        message = check_message
                        break
                else:
                    wait_min = int(re.findall("[0-9]{1,2} minutes", message.content)[0].replace(" minutes", ""))
                    self.bot.logger.info(f"NOT FOUND PASSWORD OWO HUNTBOT - WAIT {wait_min}MINS")
                    await asyncio.sleep(wait_min*60)
            if len(message.attachments) > 0:
                solve_text = self.hbcaptcha.gettext(await self.hbcaptcha.solver(message.attachments[0].url))
                await self.bot.channel.send(f"{self.configs['owo_prefix']} hb {self.configs['enables']['huntbot']} {solve_text}")
                message = await self.bot.wait_for('message', check=check, timeout=5)
                wait_time = re.findall("[0-9]{0,2}H{0,1} {0,1}[0-9]{1,2}M", message.content)[0]
                wait_sec = int(re.findall("[0-9]{1,2}M",wait_time)[0].replace("M", ""))*60
                if "H" in wait_time:
                    wait_sec += int(re.findall("[0-9]{0,2}H",wait_time)[0].replace("H", ""))*60*60
                self.bot.logger.info(f"OWO HUNTBOT SEND {self.configs['enables']['huntbot']}. WILL BACK IN {wait_time}")
                await asyncio.sleep(wait_sec)

    @tasks.loop(seconds=3)
    async def text_exp(self):
        if not self.captcha:
            await self.cooldown_command()
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://fakerapi.it/api/v1/texts?_quantity=1?&_characters={random.randint(25,150)}") as resp:
                    dt = await resp.json()
                    if dt["status"] == "OK":
                        await self.bot.channel.send(dt["data"][0]["content"])
                        self.bot.logger.info("OWO RANDOM TEXT EXP")
            await asyncio.sleep(random.randint(30,120))

    @tasks.loop(seconds=3)
    async def text_owo(self):
        if not self.captcha:
            await self.cooldown_command()
            await self.bot.channel.send("owo")
            self.bot.logger.info("TEXT OWO")
            await asyncio.sleep(random.randint(30,120))

    async def cog_load(self) -> None:
        for c in self.configs["giveaway_channels"]:
            channel = self.bot.get_channel(c)
            if not channel is None:
                async for message in channel.history(limit=5):
                    if len(message.components) > 0 and message.author.id == self.configs["owo_id"] and not message.id in self.caches["giveaway_join"]:
                        if isinstance(message.components[0], discord.ActionRow):
                            for cd in message.components[0].children:
                                if isinstance(cd, discord.Button) and not cd.disabled:
                                    await cd.click()
                                    self.caches["giveaway_join"].append(message.id)
                                    self.bot.logger.info(f"JOIN GIVEAWAY {message.id}")
        with open("extensions/owo/_caches.json", "w") as f:
            json.dump(self.caches, f)

    @commands.Cog.listener()
    async def on_message(self, message) -> None:
        if message.channel.id in self.configs["giveaway_channels"]:
            if len(message.components) > 0 and message.author.id == self.configs["owo_id"] and not message.id in self.caches["giveaway_join"]:
                if isinstance(message.components[0], discord.ActionRow):
                    if isinstance(cd, discord.Button) and not cd.disabled:
                        await cd.click()
                        self.caches["giveaway_join"] = self.caches["giveaway_join"].append(message.id)
                        with open("extensions/owo/_caches.json", "w") as f:
                            json.dump(self.owo.caches, f)
                        self.bot.logger.info(f"JOIN GIVEAWAY {message.id}")

async def setup(bot: Bot) -> None:
    await bot.add_cog(OwO(bot))