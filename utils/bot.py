import logging
from discord.ext import commands
from datetime import datetime
from twocaptcha import TwoCaptcha
class Bot(commands.Bot):
    def __init__(self, configs, *args, **kwargs) -> None:
        if configs['2captcha_api'] != "":
            self.solver = TwoCaptcha(configs['2captcha_api'])
        self.configs = configs
        self.channel = None
        self.time_onload = datetime.utcnow()
        self.logger = logging.getLogger("discord")
        super().__init__(*args, **kwargs)