import os
import glob
import time
import discord
import threading
import logging
import json
from utils.bot import Bot
from utils.webhook import BotWebhook

print("██╗  ██╗██╗   ██╗██████╗ ██╗ ██████╗")
print("██║  ██║╚██╗ ██╔╝██╔══██╗██║██╔════╝")
print("███████║ ╚████╔╝ ██████╔╝██║██║     ")
print("██╔══██║  ╚██╔╝  ██╔══██╗██║██║     ")
print("██║  ██║   ██║   ██║  ██║██║╚██████╗")
print("╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝ ╚═════╝")
print("Thanks aduck(ahihiyou20) and conan(edogawa_conan00) support me")
print("Hyric is free 100% and open source")

with open("configs.json", "r") as f:
    configs = json.load(f)

threads = []
discord.utils.setup_logging()

def runbot(bot, token):
    @bot.event
    async def on_ready():
        bot.logger = logging.getLogger(bot.user.display_name)
        bot.webhook = BotWebhook(bot.configs, bot.logger)
        logfile = logging.FileHandler(f"logs/log_{bot.user.display_name}.log", "w", "utf-8")
        logfile.setFormatter(logging.Formatter(f"{bot.user.display_name} - %(levelname)s - %(message)s"))
        bot.logger.addHandler(logfile)
        for extension in glob.glob("extensions/**"):
            for extension_file in sorted(glob.glob(f"{extension}/**/*.py", recursive=True)):
                try:
                    await bot.load_extension(extension_file.replace(".py", "").replace(os.sep, "."))
                except Exception as e:
                    bot.logger.error(e)
            bot.logger.info(f"Load extension {extension}")

    bot.run(token, log_handler=None)

for account in configs["accounts"]:
    bot = Bot(command_prefix=account["command_prefixs"], configs=configs, account=account, self_bot=True)
    thread = threading.Thread(target=runbot, daemon=True, args=(bot, account["token"]))
    thread.start()
    threads.append(thread)
    time.sleep(0.5)

for therad in threads: 
    therad.join()