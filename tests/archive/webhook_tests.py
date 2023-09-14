import asyncio
import json

import aiohttp
from discord import Webhook

with open("../../config.json") as f:
    config = json.load(f)

channel_id = config["diskord_channel_id"]
webhook_url = config["webhook_url"]
webhook_avatar_url = config["webhook_avatar_url"]


# send sample webhook
async def message_1():
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(webhook_url, session=session)
        message_content = "Message 1"

        message = await webhook.send(content=message_content, username="Maev's helper",
                                     avatar_url="https://xhost.maev.site/icons/github_logo.png", wait=True)

        return message.id


# edit message_1
async def message_2(message_id):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(webhook_url, session=session)
        message_content = "t2"
        await webhook.edit_message(message_id=message_id, content=message_content)


message_1_id = asyncio.run(message_1())
asyncio.run(message_2(message_1_id))
