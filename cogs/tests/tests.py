import asyncio
import pytz
import json
import aiohttp
import discord
from datetime import datetime
from discord import Webhook

with open("config.json") as f:
    config = json.load(f)
webhook_url = config["webhook_url"]

def current_time():
    gmt_plus_3 = pytz.timezone('Etc/GMT-3')
    current_time = datetime.now(gmt_plus_3)
    return current_time

async def foo():
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(webhook_url, session=session)
        embed = discord.Embed(colour=discord.Color.purple(), title="File upload", timestamp=current_time(), description="""
                        **New file uploaded**
                        Filename: `jdhdj.png`
                        Id: `636hdb3b2`
                        Filetype: `zip` 🗃️
                        Filesize: `123.74 mbs`
                        Chunks: `74`
                        """)
        embed.set_image(
            url="https://media.discordapp.net/attachments/1148598158721564834/1148598159858208818/Screenshot_2023-09-05_153451.jpg?width=664&height=341")
        embed.set_thumbnail(url="https://xhost.maev.site/icons/github_logo.png")

        await webhook.send(embed=embed, username="Maev's helper", avatar_url="https://xhost.maev.site/icons/github_logo.png")


asyncio.run(foo())

################################################

# import requests
# import json
#
# with open("config.json") as f:
#     config = json.load(f)
# webhook_url = config["webhook_url"]
#
# thread_id = 1148688795844218880
#
# message = {
#     "content": "This is a message to a thread.",
# }
#
# requests.post(
#     webhook_url,
#     headers={"Content-Type": "application/json"},
#     data=json.dumps(message),
#     params={"thread_id": thread_id},
# )
