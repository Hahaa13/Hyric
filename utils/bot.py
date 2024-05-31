import logging
from discord.ext import commands
from datetime import datetime
class Bot(commands.Bot):
    def __init__(self, configs, *args, **kwargs) -> None:
        self.configs = configs
        self.channel = None
        self.time_onload = datetime.utcnow()
        self.logger = logging.getLogger("discord")
        super().__init__(*args, **kwargs)