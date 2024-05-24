import glob
import re
import io
import aiohttp
import numpy as np
from PIL import Image

class Gem:
    def __init__(self, bot, configs) -> None:
        """
        self.gems[0] = gem 1
        self.gems[1] = gem 3
        self.gems[2] = gem 4
        self.gems[3] = star gem
        """
        self.ready = False
        self.bot = bot
        self.configs = configs
        self.gems = [[],[],[],[]]
        self.mapping = {"⁰":"0","¹":"1","²":"2","³":"3","⁴":"4","⁵":"5","⁶":"6","⁷":"7","⁸":"8","⁹":"9"}

    async def gem_data_collect(self, channel) -> None:
        await channel.send(f"{self.configs['owo_prefix']} inv")
        self.bot.logger.info("OWO INVENTORY")
        def check(m) -> bool:
            return m.author.id == self.configs["owo_id"] and m.channel.id == self.bot.channel.id and self.bot.user.display_name in m.content
        message = await self.bot.wait_for('message', check=check, timeout=5)
        content = message.content
        if "050" in content and self.configs["use_lootbox"]:
            await channel.send(f"{self.configs['owo_prefix']} lb all")
        for k,v in self.mapping.items():
            content = content.replace(k,v)
        gemtypes = ["gem1", "gem3", "gem4", "star"]
        for gem in gemtypes:
            for agem in re.findall("`[0-9]{1,3}`<:[a-z]"+gem+":[0-9]{1,20}>[0-9]{1,999999}",content):
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
            await message.channel.send(f"{self.configs['owo_prefix']} use " + " ".join(usegems))
            self.bot.logger.info("OWO USE " + " ".join(usegems))

class HuntBotCaptcha:
    def __init__(self) -> None:
        self.checks = []
        check_images = glob.glob("extensions/owo/huntbot_letter/**/*.png")
        for check_image in sorted(check_images):
            img = Image.open(check_image)
            self.checks.append((img, img.size, check_image.split(".")[0].split("/")[-1]))
            
    async def solver(self, captcha_url: str) -> list:
        async with aiohttp.ClientSession() as session:
            async with session.get(captcha_url) as resp:
                large_array = np.array(Image.open(io.BytesIO(await resp.read())))
        matches = []
        for check in self.checks:
            small_array = np.array(check[0])
            large_h, large_w = large_array.shape[:2]
            small_h, small_w = small_array.shape[:2]
            for y in range(large_h - small_h + 1):
                for x in range(large_w - small_w + 1):
                    segment = large_array[y:y + small_h, x:x + small_w]
                    mask = (small_array[:, :, 3] > 0) 
                    if np.array_equal(segment[mask], small_array[mask]):
                        overlap = False
                        for m in matches:
                            if (m[0] - check[1][0] < x < m[0] + check[1][0]) and (m[1] - check[1][1] < y < m[1] + check[1][1]):
                                overlap = True
                                break
                        if not overlap:
                            matches.append((x, y, check[2]))
        return sorted(matches,key=lambda tup: tup[0])

    def gettext(self, matches: list) -> str:
        return "".join([i[2] for i in matches])

async def setup(bot) -> None:
    pass