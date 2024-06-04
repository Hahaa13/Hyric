import os
import glob
import discord
import json
from utils.bot import Bot

with open("configs.json", "r") as f:
    configs = json.load(f)
bot = Bot(command_prefix=configs["command_prefixs"], configs=configs, self_bot=True)

@bot.event
async def on_ready():
    print("""
██╗  ██╗██╗   ██╗██████╗ ██╗ ██████╗
██║  ██║╚██╗ ██╔╝██╔══██╗██║██╔════╝
███████║ ╚████╔╝ ██████╔╝██║██║     
██╔══██║  ╚██╔╝  ██╔══██╗██║██║     
██║  ██║   ██║   ██║  ██║██║╚██████╗
╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝ ╚═════╝""")
    for extension in glob.glob("extensions/**"):
        for extension_file in sorted(glob.glob(f"{extension}/**/*.py", recursive=True)):
            try:
                await bot.load_extension(extension_file.replace(".py", "").replace(os.sep, "."))
            except Exception as e:
                bot.logger.error(e)
        bot.logger.info(f"Load extension {extension}")

if __name__ == "__main__":
    bot.run(configs["token"])