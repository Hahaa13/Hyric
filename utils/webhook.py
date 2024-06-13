from aiohttp import ClientSession
from discord import Colour
from discord import Embed
from discord import User
from discord import Webhook

class BotWebhook:
    def __init__(self, configs: dict, logger) -> None:
        self.webhook_url = configs["webhook_url"]
        self.wbh = None
        self.logger = logger
        self.configs = configs

    async def setup(self):
        if not self.webhook_url:
            return
        async with ClientSession() as session:
            self.wbh = Webhook.from_url(self.webhook_url, session=session)

    async def send(self, user: User, title: str = None, description: str = None, ping: bool = False, colour: Colour = Colour.random()) -> None:
        if self.wbh:
            embed = Embed(title=title, description=description, colour=colour)
            embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
            content = f"<@{user.id}> " + " ".join([f"<@{user}>" for user in self.configs["user_ping_webhook"]]) if ping else None
            await self.wbh.send(content=content, embed=embed)
            return
        self.logger.warning("WEBHOOK NOT FOUND AND MESSAGE WILL NOT SEND")