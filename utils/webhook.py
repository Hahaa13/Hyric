from aiohttp import ClientSession
from discord import Colour
from discord import Embed
from discord import User
from discord import Webhook

class BotWebhook:
    def __init__(self, url) -> None:
        self.webhook_url = url
    
    async def send(self, user: User, title: str = None, description: str = None, ping: bool = False, colour: Colour = Colour.random()) -> None:
        if self.webhook_url:
            embed = Embed(title=title, description=description, colour=colour)
            embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
            content = f"<@{user.id}>" if ping else None
            async with ClientSession() as session:
                wbh = Webhook.from_url(self.webhook_url, session=session)
                await wbh.send(content=content, embed=embed)