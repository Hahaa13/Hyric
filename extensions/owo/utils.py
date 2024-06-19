import glob
import os
import re
import io
import asyncio
import aiohttp
import numpy as np
from PIL import Image
from utils.bot import Bot

class Quest:
    def __init__(self, owo, quest: list) -> None:
        self.bot = owo.bot
        self.owo = owo
        self.configs = self.owo.configs
        self.cooldown_command = owo.cooldown_command
        self.quest = quest
        self.quest_id = re.findall("([1-3]).", quest[0])[0]

    def sort_quest(quests: list, rewards: list, progress: list) -> tuple:
        for quest1, reward1, pgs1 in zip(quests, rewards, progress):
            questr1 = re.sub(r'\d+', '{}', quest1)
            for quest2, reward2, pgs2 in zip(quests, rewards, progress):
                questr2 = re.sub(r'\d+', '{}', quest2)
                questrs = [re.sub(r'\d+', '{}', quest) for quest in quests]
                if questr1 == questr2 and (questrs.count(questr1) > 1 or questrs.count(questr2) > 1) and pgs1 in progress and pgs2 in progress:
                    if pgs1 < pgs2:
                        quests.remove(quest1)
                        rewards.remove(reward1)
                        progress.remove(pgs1)
                        continue
                    quests.remove(quest2)
                    rewards.remove(reward2)
                    progress.remove(pgs2)
        return (quests, rewards, progress)

    def candone(self) -> bool:
        for allow_reward in self.configs["quest_rewards_allow"]:
            if f":{allow_reward}:" in self.quest[2]:
                return True
        return False

    async def reroll(self) -> None:
        await self.cooldown_command()
        await self.bot.channel.send(f"{self.configs['owo_prefix']} quest rr {self.quest_id}")
        self.bot.logger.info(f"OWO QUEST REROLL {self.quest_id}")

    async def gamble_quest(self) -> None:
        running = self.owo.coinflip.is_running()
        if not running:
            self.owo.configs["coinflip_rate"] = 1
            self.owo.configs["enables"]["coinflip"] = 1
            self.owo.coinflip_cow = 1
            self.owo.coinflip.start()
        while self.quest[1] >= self.owo.coinflip.current_loop:
            await asyncio.sleep(3)
        else:
            if not running:
                self.owo.coinflip.stop()
            self.bot.logger.info(f"QUEST {self.quest_id} DONE")

    async def say_owo(self) -> None:
        running = self.owo.text_owo.is_running()
        if not running:
            self.owo.text_owo.start()
        while self.quest[1] >= self.owo.text_owo.current_loop:
            await asyncio.sleep(3)
        else:
            if not running:
                self.owo.text_owo.stop()
            self.bot.logger.info(f"QUEST {self.quest_id} DONE")
    
    async def use_action(self) -> None:
        if len(self.bot.bots) < 2: return
        loop_counts = 0
        tasks = []
        while self.quest[1] >= loop_counts:
            for otherbot in self.bot.bots:
                if self.bot != otherbot:
                    owo = otherbot.get_cog("OwO")
                    if owo and not owo.use_action_command.is_running():
                        owo.configs["use_action_command_target"] = self.bot.user.id
                        owo.use_action_command.start()
                        tasks.append(owo.use_action_command)
            loop_counts = 0
            for task in tasks:
                loop_counts += task.current_loop
            await asyncio.sleep(3)
        else:
            for task in tasks:
                task.stop()
            self.bot.logger.info(f"QUEST {self.quest_id} DONE")
    
    async def pray_or_curse(self, poc: str) -> None:
        if len(self.bot.bots) < 2: return
        loop_counts = 0
        tasks = []
        while self.quest[1] >= loop_counts:
            for otherbot in self.bot.bots:
                if otherbot != self.bot:
                    owo = otherbot.get_cog("OwO")
                    if owo and not owo.configs["pray_or_curse_id"]:
                        owo.configs["enables"]["pray_or_curse"] = poc
                        owo.configs["pray_or_curse_id"] = self.bot.user.id
                        running = owo.pray_or_curse.is_running()
                        poc_target = owo.configs["enables"]["pray_or_curse"]
                        if not running:
                            owo.pray_or_curse.start()
                        tasks.append((owo.pray_or_curse, running, owo, poc_target))
            loop_counts = 0
            for task in tasks:
                loop_counts += task[0].current_loop
            await asyncio.sleep(3)
        else:
            for task in tasks:
                task[2].configs["pray_or_curse_id"] = False
                task[2].configs["enables"]["pray_or_curse"] = task[3]
                if not task[1]:
                    task[0].stop()
            self.bot.logger.info(f"QUEST {self.quest_id} DONE")

class Gem:
    def __init__(self, bot, cooldown_command, configs) -> None:
        """
        self.gems[0] = gem 1
        self.gems[1] = gem 3
        self.gems[2] = gem 4
        self.gems[3] = star gem
        """
        self.ready = False
        self.bot = bot
        self.cooldown_command = cooldown_command
        self.configs = configs
        self.gems = ([],[],[],[])
        self.mapping = {"⁰":"0","¹":"1","²":"2","³":"3","⁴":"4","⁵":"5","⁶":"6","⁷":"7","⁸":"8","⁹":"9"}
    
    def _check(self, m) -> bool:
        return m.author.id == self.configs["owo_id"] and m.channel.id == self.bot.channel.id and self.bot.user.display_name in m.content

    async def gem_data_collect(self, channel) -> None:
        await self.cooldown_command()
        await channel.send(f"{self.configs['owo_prefix']} inv")
        self.bot.logger.info("OWO INVENTORY")
        message = await self.bot.wait_for('message', check=self._check, timeout=10)
        content = message.content
        if "050" in content and self.configs["use_lootbox"]:
            await self.cooldown_command()
            await channel.send(f"{self.configs['owo_prefix']} lb all")
            self.bot.logger.info("OWO LOOTBOX")
            await self.cooldown_command()
            await channel.send(f"{self.configs['owo_prefix']} inv")
            self.bot.logger.info("OWO INV")
            message = await self.bot.wait_for("message", check=self._check, timeout=10)
        content = message.content
        for k,v in self.mapping.items():
            content = content.replace(k,v)
        gemtypes = ["gem1", "gem3", "gem4", "star"]
        for gem in gemtypes:
            for agem in re.findall("`[0-9]{1,3}`<a{0,1}:[a-z]"+gem+":[0-9]{1,20}>[0-9]{1,999999}",content):
                self.gems[gemtypes.index(gem)].append([agem.split("`")[1], int(agem.split(">")[-1])])
        self.ready = True

    def _huntgems(self, content: str) -> list:
        return ["gem1:" in content, "gem3:" in content, "gem4:" in content, "star:" in content]

    async def on_hunt(self, message) -> None:
        agems = self._huntgems(message.content)
        usegems = []
        gem_sort = 0 if self.configs["gem_sort"].lower() == "low" else -1
        count = 0
        for gem in agems:
            if not gem and len(self.gems[count]) > 0 and (not count == 3 or self.configs["use_star_gem"]):
                usegems.append(self.gems[count][gem_sort][0])
                self.gems[count][gem_sort][1] -= 1
                if self.gems[count][gem_sort][1] < 1:
                    del self.gems[count][gem_sort]
            count += 1
        if usegems != [] and self.ready:
            await self.cooldown_command()
            await message.channel.send(f"{self.configs['owo_prefix']} use " + " ".join(usegems))
            self.bot.logger.info("OWO USE " + " ".join(usegems))

class HuntBotCaptcha:
    def __init__(self) -> None:
        self.checks = []
        check_images = glob.glob("extensions/owo/huntbot_letter/**/*.png")
        for check_image in sorted(check_images):
            img = Image.open(check_image)
            self.checks.append((img, img.size, check_image.split(".")[0].split(os.sep)[-1]))
            
    async def solver(self, captcha_url: str) -> list:
        async with aiohttp.ClientSession() as session:
            async with session.get(captcha_url) as resp:
                large_image = Image.open(io.BytesIO(await resp.read()))
                large_array = np.array(large_image)

        matches = []
        for img, (small_w, small_h), letter in self.checks:
            small_array = np.array(img)
            mask = small_array[:, :, 3] > 0
            for y in range(large_array.shape[0] - small_h + 1):
                for x in range(large_array.shape[1] - small_w + 1):
                    segment = large_array[y:y + small_h, x:x + small_w]
                    if np.array_equal(segment[mask], small_array[mask]):
                        if not any((m[0] - small_w < x < m[0] + small_w) and (m[1] - small_h < y < m[1] + small_h) for m in matches):
                            matches.append((x, y, letter))
        return sorted(matches, key=lambda tup: tup[0])

    def gettext(self, matches: list) -> str:
        return "".join([i[2] for i in matches])

async def setup(bot) -> None:
    pass