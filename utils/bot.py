import logging
from utils.webhook import BotWebhook
from discord.ext import commands
from datetime import datetime

class Bot(commands.Bot):
    def __init__(self, configs, *args, **kwargs) -> None:
        self.configs = configs
        self.channel = None
        self.time_onload = datetime.utcnow()
        self.logger = logging.getLogger("discord")
        self.webhook = BotWebhook(configs["webhook_url"], self.logger)
        self.logger.addHandler(logging.FileHandler(filename='latest.log', encoding='utf-8', mode='w'))
        super().__init__(*args, **kwargs)

    async def close(self) -> None:
        self.logger.info("BOT STOP")