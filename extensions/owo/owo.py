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
        self.pause = False
        self.lock = asyncio.Lock()
        self.hbcaptcha = HuntBotCaptcha()
        self.configs = json.load(open("extensions/owo/_configs.json"))
        self.caches = json.load(open(f"extensions/owo/caches/{self.bot.user.id}_cache.json")) if os.path.exists(f"extensions/owo/caches/{self.bot.user.id}_cache.json") else {"time": 0, "giveaway_join": [], "checks": {"daily": False, "cookie": False, "run": False, "pup": False, "piku": False, "quest_reroll": False}}
        self.gem = Gem(bot, self.cooldown_command, self.configs)
        self.slot_cow = self.configs["enables"]["slot"] if self.configs["enables"]["slot"] else 0
        self.coinflip_cow = self.configs["enables"]["coinflip"] if self.configs["enables"]["coinflip"] else 0
        self.blackjack_cow = self.configs["enables"]["blackjack"] if self.configs["enables"]["blackjack"] else 0
        fuctions = [self.sleep, self.hunt, self.battle, self.daily, self.pray_or_curse, self.sell, self.sac, self.cookie, self.run, self.pup, self.piku, self.text_exp, self.text_owo, self.coinflip, self.slot, self.blackjack, self.buy, self.owo_delay_check, self.huntbot]
        enables = ["auto_sleep", "hunt", "battle", "daily", "pray_or_curse", "sell", "sac", "cookie", "run", "pup", "piku", "text_exp", "text_owo", "coinflip", "slot", "blackjack", "buy", "delay_check", "huntbot"]
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
            while self.pause or self.captcha:
                await asyncio.sleep(3)
            await asyncio.sleep(random.randint(3,5))

    def addCache(self, key) -> None:
        self.caches["checks"][key] = True
        with open(f"extensions/owo/caches/{self.bot.user.id}_cache.json", "w") as f:
            json.dump(self.caches, f)
    
    @tasks.loop(minutes=3)
    async def owo_delay_check(self):
        if not (self.captcha or self.pause):
            async for message in self.bot.channel.history(limit=10):
                if message.author.id == self.configs["owo_id"]:
                    self.bot.logger.info("OWO DELAY CHECK - ONLINE")
                    break
            else:
                if self.configs["better_delay_check"]:
                    await self.cooldown_command()
                    await self.bot.channel.send(f"{self.configs['owo_prefix']} ping")
                    def check(m) -> bool:
                        return m.author.id == self.configs["owo_id"] and m.channel.id == self.bot.channel.id and "🏓" in m.content
                    try:
                        await self.bot.wait_for("message", check=check, timeout=10)
                        return
                    except asyncio.TimeoutError or TimeoutError: pass
                self.pause = True
                self.bot.logger.warning("OWO IS DELAY. BOF WILL SLEEP 10MINS")
                await asyncio.sleep(600)
                self.pause = False

    @tasks.loop(seconds=3)
    async def sleep(self):
        await asyncio.sleep(self.configs["sleep_delay"])
        self.bot.logger.info("OWO SLEEP ON")
        self.pause = True
        await asyncio.sleep(self.configs["sleep_time"])
        while self.captcha:
            await asyncio.sleep(3)
        self.bot.logger.info("OWO SLEEP OFF")
        self.pause = False

    @tasks.loop(seconds=3)
    async def cachemanager(self) -> None:
        now = datetime.datetime.utcnow()
        old = datetime.datetime.fromtimestamp(self.caches["time"])
        if old.hour < 7 or now.day > old.day or now.month > old.month or now.year > old.year:
            if now.hour >= 7 or now.day - old.day > 1:
                self.bot.logger.info("RESET CACHES")
                self.caches["time"] = now.timestamp()
                for k in self.caches["checks"].keys():
                    self.caches["checks"][k] = False
                with open(f"extensions/owo/caches/{self.bot.user.id}_cache.json", "w") as f:
                    json.dump(self.caches, f)
                return
        await asyncio.sleep(self.getTimeCooldown())

    @tasks.loop(seconds=3)
    async def hunt(self) -> None:
        await self.cooldown_command()
        await self.bot.channel.send(f"{self.configs['owo_prefix']} hunt")
        def check(m) -> bool:
            return m.author.id == self.configs["owo_id"] and m.channel.id == self.bot.channel.id and f"**🌱 | {self.bot.user.display_name}**" in m.content
        message = await self.bot.wait_for('message', check=check, timeout=10)
        xp = re.findall("[0-9]{1,99}xp", message.content)[0]
        self.bot.logger.info(f"OWO HUNT - {xp.upper()}")
        if self.configs["use_gem"]:
            if not self.gem.ready or (self.configs["use_lootbox"] and ":box:" in message.content):
                await self.gem.gem_data_collect(self.bot.channel)
            await self.gem.on_hunt(message)
        await asyncio.sleep(random.randint(18,25))

    @tasks.loop(seconds=3)
    async def battle(self) -> None:
        await self.cooldown_command()
        await self.bot.channel.send(f"{self.configs['owo_prefix']} battle")
        self.bot.logger.info("OWO BATTLE")
        await asyncio.sleep(random.randint(18,25))
    
    @commands.Cog.listener("on_message")
    async def on_message_1(self, message) -> None:
        if self.configs["auto_join_battle"]:
            if message.author.id == self.configs["owo_id"] and f"<@{self.bot.user.id}>" == message.content and len(message.components) == 1 and len(message.embeds) > 0:
                cd = message.components[0].children[0] if self.configs["auto_join_battle"].lower() == "accept" else message.components[0].children[1]
                await cd.click()
                self.bot.logger.info(f"JOIN BATTLE {message.id}")

    @tasks.loop(seconds=3)
    async def daily(self) -> None:
        if self.caches["checks"]["daily"]:
            await asyncio.sleep(self.getTimeCooldown() + 10)
        await self.cooldown_command()
        await self.bot.channel.send(f"{self.configs['owo_prefix']} daily")
        timesec = self.getTimeCooldown()
        def check(m) -> bool:
            return m.author.id == self.configs["owo_id"] and m.channel.id == self.bot.channel.id and self.bot.user.display_name in m.content
        message = await self.bot.wait_for('message', check=check, timeout=10)
        if f"**⏱ |** Nu! **{self.bot.user.display_name}**!" in message.content:
            self.bot.logger.info(f"DAILY COOLDOWN {timesec}s")
        elif f"💰 **| {self.bot.user.display_name}**, Here is your daily " in message.content:
            self.bot.logger.info(f"DAILY CLAIMED, NEXT DAILY IN {timesec}s")
        self.addCache("daily")
        await asyncio.sleep(timesec)

    @tasks.loop(seconds=3)
    async def pray_or_curse(self):
        await self.cooldown_command()
        poc_user = ""
        if self.configs["pray_or_curse_id"]:
            poc_user = f"<@{self.configs['pray_or_curse_id']}>"
        await self.bot.channel.send(f"{self.configs['owo_prefix']} {self.configs['enables']['pray_or_curse']} {poc_user}")
        def check(m) -> bool:
            return m.author.id == self.configs["owo_id"] and m.channel.id == self.bot.channel.id and (str(self.bot.user.id) in m.content or self.bot.user.name in m.content or self.bot.user.display_name in m.content) and ("pray" in m.content or "curse" in m.content or "⏱" in m.content)
        try:
            message = await self.bot.wait_for("message", check=check, timeout=10)
        except asyncio.TimeoutError:
            await asyncio.sleep(310)
            return
        if "⏱" in message.content:
            waitime = int(re.findall(":([0-9]{8,18})", message.content)[0])
            self.bot.logger.info(f"OWO {self.configs['enables']['pray_or_curse'].upper()} {poc_user} COOLDOWN")
            await asyncio.sleep(waitime - datetime.datetime.utcnow().timestamp() + 5)
            return
        self.bot.logger.info(f"OWO {self.configs['enables']['pray_or_curse'].upper()} {poc_user}")
        await asyncio.sleep(random.randint(310, 360))

    @tasks.loop(seconds=3)
    async def sell(self) -> None:
        await self.cooldown_command()
        await self.bot.channel.send(f"{self.configs['owo_prefix']} sell {self.configs['enables']['sell']}")
        def check(m) -> bool:
            return m.author.id == self.configs["owo_id"] and m.channel.id == self.bot.channel.id and f"**🔪 | {self.bot.user.display_name}** sold" in m.content
        message = await self.bot.wait_for('message', check=check, timeout=10)
        cow = re.findall(" [0-9]{1,99}", message.content)[0]
        self.bot.logger.info(f"OWO SELL {self.configs['enables']['sell'].upper()} -{cow} COW")
        await asyncio.sleep(random.randint(600, 650))

    @tasks.loop(seconds=3)
    async def sac(self) -> None:
        await self.cooldown_command()
        await self.bot.channel.send(f"{self.configs['owo_prefix']} sac {self.configs['enables']['sac']}")
        def check(m) -> bool:
            return m.author.id == self.configs["owo_id"] and m.channel.id == self.bot.channel.id and f"**🔪 | {self.bot.user.display_name}** sacrificed" in m.content
        message = await self.bot.wait_for('message', check=check, timeout=10)
        sac = re.findall(" [0-9]{1,99}", message.content)[0]
        self.bot.logger.info(f"OWO SAC {self.configs['enables']['sac'].upper()} -{sac} SACRIFICED")
        await asyncio.sleep(random.randint(600, 650))

    @tasks.loop(seconds=3)
    async def cookie(self) -> None:
        if self.caches["checks"]["cookie"]:
            await asyncio.sleep(self.getTimeCooldown() + 10)
        await self.cooldown_command()
        await self.bot.channel.send(f"{self.configs['owo_prefix']} cookie <@{self.configs['enables']['cookie']}>")
        self.bot.logger.info(f"OWO COOKIE {self.configs['enables']['cookie']}")
        self.addCache("cookie")
        await asyncio.sleep(self.getTimeCooldown())

    @tasks.loop(seconds=3)
    async def run(self) -> None:
        if self.caches["checks"]["run"]:
            await asyncio.sleep(self.getTimeCooldown() + 10)
        await self.cooldown_command()
        await self.bot.channel.send(f"{self.configs['owo_prefix']} run")
        def check(m) -> bool:
            return m.author.id == self.configs["owo_id"] and m.channel.id == self.bot.channel.id and "run" in m.content
        message = await self.bot.wait_for('message', check=check, timeout=10)
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
        if self.caches["checks"]["pup"]:
            await asyncio.sleep(self.getTimeCooldown() + 10)
        await self.cooldown_command()
        await self.bot.channel.send(f"{self.configs['owo_prefix']} pup")
        def check(m) -> bool:
            return m.author.id == self.configs["owo_id"] and m.channel.id == self.bot.channel.id and "pup" in m.content
        message = await self.bot.wait_for('message', check=check, timeout=10)
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
        if self.caches["checks"]["piku"]:
            await asyncio.sleep(self.getTimeCooldown() + 10)
        await self.cooldown_command()
        await self.bot.channel.send(f"{self.configs['owo_prefix']} piku")
        def check(m) -> bool:
            return m.author.id == self.configs["owo_id"] and m.channel.id == self.bot.channel.id and "carrot" in m.content
        message = await self.bot.wait_for('message', check=check, timeout=10)
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
        await self.cooldown_command()
        await self.bot.channel.send(f"{self.configs['owo_prefix']} hb {self.configs['enables']['huntbot']}")
        def check(m) -> bool:
            return m.author.id == self.configs["owo_id"] and m.channel.id == self.bot.channel.id and ("bot:" in m.content or "password" in m.content)
        message = await self.bot.wait_for('message', check=check, timeout=10)
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
            if self.configs["enables"]["upgrade_huntbot"]:
                utype = random.choice(self.configs["enables"]["upgrade_hunbot"]) if len(self.configs["enables"]["upgrade_huntbot"]) > 1 else self.configs["enables"]["upgrade_huntbot"][0]
                await self.cooldown_command()
                await self.bot.channel.send(f"{self.configs['owo_prefix']} upgrade {utype} all")
                self.bot.logger.info(f"OWO UPGRADE {utype.upper()}")
            await self.cooldown_command()
            await self.bot.channel.send(f"{self.configs['owo_prefix']} hb {self.configs['enables']['huntbot']} {solve_text}")
            message = await self.bot.wait_for('message', check=check, timeout=10)
            wait_time = re.findall("[0-9]{0,2}H{0,1} {0,1}[0-9]{1,2}M", message.content)[0]
            wait_sec = int(re.findall("[0-9]{1,2}M",wait_time)[0].replace("M", ""))*60
            if "H" in wait_time:
                wait_sec += int(re.findall("[0-9]{0,2}H",wait_time)[0].replace("H", ""))*60*60
            self.bot.logger.info(f"OWO HUNTBOT SEND {self.configs['enables']['huntbot']}. WILL BACK IN {wait_time}")
            await asyncio.sleep(wait_sec)

    @tasks.loop(seconds=3)
    async def text_exp(self):
        await self.cooldown_command()
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://fakerapi.it/api/v1/texts?_quantity=1?&_characters={random.randint(25,150)}") as resp:
                dt = await resp.json()
                if dt and dt["status"] == "OK":
                    await self.bot.channel.send(dt["data"][0]["content"])
                    self.bot.logger.info("OWO RANDOM TEXT EXP")
                else:
                    self.bot.logger.warning("OWO RANDOM TEXT API DOWN")
        await asyncio.sleep(random.randint(60, 120))

    @tasks.loop(seconds=3)
    async def text_owo(self):
        await self.cooldown_command()
        await self.bot.channel.send(random.choice(["OwO", "UwU", "owo", "uwu"]))
        self.bot.logger.info("TEXT OWO")
        await asyncio.sleep(random.randint(60,120))

    async def cog_load(self) -> None:
        if self.configs['enables']['quests']:
            asyncio.create_task(self.quests())
        for c in self.configs["giveaway_channels"]:
            channel = self.bot.get_channel(c)
            if not channel is None:
                async for message in channel.history(limit=5):
                    if len(message.components) > 0 and message.author.id == self.configs["owo_id"] and not message.id in self.caches["giveaway_join"]:
                        if isinstance(message.components[0], discord.ActionRow):
                            cd = message.components[0].children[0]
                            if isinstance(cd, discord.Button) and not cd.disabled:
                                await cd.click()
                                self.caches["giveaway_join"].append(message.id)
                                with open(f"extensions/owo/caches/{self.bot.user.id}_cache.json", "w") as f:
                                    json.dump(self.caches, f)
                                self.bot.logger.info(f"JOIN GIVEAWAY {message.id}")

    @commands.Cog.listener()
    async def on_message(self, message) -> None:
        if message.channel.id in self.configs["giveaway_channels"]:
            if len(message.components) > 0 and message.author.id == self.configs["owo_id"] and not message.id in self.caches["giveaway_join"]:
                if isinstance(message.components[0], discord.ActionRow):
                    cd = message.components[0].children[0]
                    if isinstance(cd, discord.Button) and not cd.disabled:
                        await cd.click()
                        self.caches["giveaway_join"].append(message.id)
                        with open(f"extensions/owo/caches/{self.bot.user.id}_cache.json", "w") as f:
                            json.dump(self.caches, f)
                        self.bot.logger.info(f"JOIN GIVEAWAY {message.id}")

    @tasks.loop(seconds=3)
    async def coinflip(self) -> None:
        await self.cooldown_command()
        await self.bot.channel.send(f"{self.configs['owo_prefix']} cf {self.coinflip_cow}")
        def check(m) -> bool:
            return m.author.id == self.configs["owo_id"] and m.channel.id == self.bot.channel.id and self.bot.user.display_name in m.content
        message = await self.bot.wait_for("message", check=check, timeout=10)
        await asyncio.sleep(random.randint(5,8))
        if "lost" in message.content:
            self.bot.logger.info(f"OWO COINFLIP LOST {self.coinflip_cow}")
            self.coinflip_cow *= self.configs["coinflip_rate"]
            if self.coinflip_cow > 250000: self.coinflip_cow = 250000
        else:
            self.bot.logger.info(f"OWO COINFLIP WON {self.coinflip_cow}")
            self.coinflip_cow = self.configs["enables"]["coinflip"]
        await asyncio.sleep(random.randint(18,25))
    
    @tasks.loop(seconds=3)
    async def slot(self):
        await self.cooldown_command()
        await self.bot.channel.send(f"{self.configs['owo_prefix']} slot {self.slot_cow}")
        def check(m) -> bool:
            return m.author.id == self.configs["owo_id"] and m.channel.id == self.bot.channel.id and self.bot.user.display_name in m.content
        message = await self.bot.wait_for("message", check=check, timeout=10)
        await asyncio.sleep(random.randint(6,8))
        if "nothing" in message.content:
            self.bot.logger.info(f"OWO SLOT LOST {self.slot_cow}")
            self.slot_cow = self.slot_cow * self.configs["slot_rate"]
            if self.slot_cow > 250000: self.slot_cow = 250000
        else:
            wincow = int(re.findall(" [0-9]{1,99}", message.content)[1].replace(" ", ""))
            self.bot.logger.info(f"OWO SLOT WON {wincow}")
            self.slot_cow = self.configs["enables"]["slot"]
        await asyncio.sleep(random.randint(18,25))
    
    @tasks.loop(seconds=3)
    async def blackjack(self):
        await self.cooldown_command()
        await self.bot.channel.send(f"{self.configs['owo_prefix']} bj {self.blackjack_cow}")
        def check(m) -> bool:
            return m.author.id == self.configs["owo_id"] and m.channel.id == self.bot.channel.id and len(m.embeds) == 1 and self.bot.user.name in m.embeds[0].author.name
        message = await self.bot.wait_for("message", check=check, timeout=10)
        while True:
            await asyncio.sleep(3)
            if "in progress" in message.embeds[0].footer.text or "resuming" in message.embeds[0].footer.text:
                point = int(re.findall("[0-9]{1,2}", message.embeds[0].fields[1].name)[0])
                if point < 17:
                    if not message.reactions[0].me:
                        await message.add_reaction("👊")
                    else:
                        await message.remove_reaction("👊", self.bot.user)
                elif point >= 17:
                    await message.add_reaction("🛑")
            elif "You won" in message.embeds[0].footer.text:
                self.bot.logger.info(f"OWO BLACKJACK WIN {self.blackjack_cow}")
                self.blackjack_cow = self.configs["enables"]["blackjack"]
                break
            elif "You lost" in message.embeds[0].footer.text:
                self.bot.logger.info(f"OWO BLACKJACK LOST {self.blackjack_cow}")
                self.blackjack_cow *= self.configs["blackjack_rate"]
                if self.blackjack_cow > 250000: self.blackjack_cow = 250000
                break
            elif "You tied" in message.embeds[0].footer.text or "You both" in message.embeds[0].footer.text:
                self.bot.logger.info(f"OWO BLACKJACK TIED")
                break
            else:
                self.bot.logger.warning(f"OWO BLACKJACK ERROR NOT FOUND")
                break
        await asyncio.sleep(random.randint(18,25))

    @tasks.loop(seconds=3)
    async def buy(self) -> None:
        await self.cooldown_command()
        bi = random.choice(self.configs["enables"]["buy"])
        await self.bot.channel.send(f"{self.configs['owo_prefix']} buy {bi}")
        self.bot.logger.info(f"OWO BUY {bi}")
        await asyncio.sleep(18,25)
    
    @tasks.loop(seconds=3)
    async def use_action_command(self) -> None:
        await self.cooldown_command()
        atype = random.choice(["wave", "kiss", "kill", "hug", "slap"])
        await self.bot.channel.send(f"{self.configs['owo_prefix']} {atype} <@{self.configs['use_action_command_target']}>")
        self.bot.logger.info(f"OWO ACTION COMMAND ({atype.upper()}) {target}")
        await asyncio.sleep(random.randint(18,25))

    async def quests(self):
        await self.cooldown_command()
        await self.bot.channel.send(f"{self.configs['owo_prefix']} quest")
        self.bot.logger.info("OWO QUEST")
        def check(m) -> bool:
            return m.author.id == self.configs["owo_id"] and m.channel.id == self.bot.channel.id and len(m.embeds) == 1 and str(self.bot.user.id) in m.embeds[0].description
        message = await self.bot.wait_for("message", check=check, timeout=10)
        quests = re.findall(r"\*\*(.*?)\*\*", message.embeds[0].description)
        rewards = re.findall(r"` [0-9]{0,10},{0,1}[0-9]{0,10} {0,1}<(:[a-z]{1,25}:)", message.embeds[0].description)
        pg = re.findall(r"\[([0-9]{1,3})/([0-9]{1,3})", message.embeds[0].description)
        progress = [int(pg[quests.index(quest)][1]) - int(pg[quests.index(quest)][0]) for quest in quests]
        quests, rewards, progress = Quest.sort_quest(quests, rewards, progress)
        for quest, reward, progres in zip(quests, rewards, progress):
            quest_handler = Quest(self, [quest, progres, reward])
            if not quest_handler.candone():
                if not self.caches["checks"]["quest_reroll"]:
                    await quest_handler.reroll()
                    self.addCache("quest_reroll")
                    return await self.quests()
            else:
                if "gamble" in quest.lower():
                    self.bot.logger.info("QUEST START GAMBLE")
                    asyncio.create_task(quest_handler.gamble_quest())
                elif "say" in quest.lower():
                    self.bot.logger.info("QUEST START SAY OWO")
                    asyncio.create_task(quest_handler.say_owo())
                elif "action command on you" in quest.lower():
                    self.bot.logger.info("QUEST START USE ACTION ON YOU")
                    asyncio.create_task(quest_handler.use_action())
                elif "curse" in quest.lower():
                    self.bot.logger.info("QUEST START CURSE")
                    asyncio.create_task(quest_handler.pray_or_curse("curse"))
                elif "pray" in quest.lower():
                    self.bot.logger.info("QUEST START PRAY")
                    asyncio.create_task(quest_handler.pray_or_curse("pray"))
async def setup(bot: Bot) -> None:
    await bot.add_cog(OwO(bot))