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

class Command:
    def is_commamd(message, bot: Bot):
        return (message.author.id in bot.account["user_allow_commands"] or message.author.id == bot.user.id) and any(message.content.startswith(p) for p in bot.command_prefix)

