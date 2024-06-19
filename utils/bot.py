import asyncio
from utils.webhook import BotWebhook
from discord.ext import commands
from datetime import datetime

class Bot(commands.Bot):
    def __init__(self, bots, account, configs, *args, **kwargs) -> None:
        self.bots = bots
        self.loop = asyncio.get_event_loop()
        self.configs = configs
        self.account = account
        self.channel = None
        self.time_onload = datetime.utcnow()
        self.logger = None
        self.webhook = None
        super().__init__(*args, **kwargs)