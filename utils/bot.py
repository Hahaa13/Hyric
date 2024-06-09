from utils.webhook import BotWebhook
from discord.ext import commands
from datetime import datetime

class Bot(commands.Bot):
    def __init__(self, account, configs, *args, **kwargs) -> None:
        self.configs = configs
        self.account = account
        self.channel = None
        self.time_onload = datetime.utcnow()
        self.logger = None
        self.webhook = None
        super().__init__(*args, **kwargs)