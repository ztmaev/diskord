import asyncio
import json
import os
from datetime import datetime

import aiohttp
import discord
import pytz
from discord import Webhook

# config.json in ../../config.json
with open("../../config.json") as f:
    config = json.load(f)
webhook_url = config["webhook_url"]


def current_time():
    gmt_plus_3 = pytz.timezone('Etc/GMT-3')
    current_time = datetime.now(gmt_plus_3)
    return current_time


async def foo():
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(webhook_url, session=session)
        embed = discord.Embed(colour=discord.Color.purple(), title="📁 File uploaded", timestamp=current_time(),
                              description="""
                        Filename: `jdhdj.png`
                        Id: `636hdb3b2`
                        Filetype: `zip`
                        Filesize: `123.74 mbs`
                        Chunks: `74`
                        """)
        embed.set_image(
            url = "https://media.discordapp.net/attachments/1148598158721564834/1148598159858208818/Screenshot_2023-09-05_153451.jpg?width=664&height=341")
        embed.set_thumbnail(url="https://xhost.maev.site/icons/github_logo.png")

        await webhook.send(embed=embed, username="Maev's helper",
                           avatar_url="https://xhost.maev.site/icons/github_logo.png")


# thread creation
async def thread_request():
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(webhook_url, session=session)
        test = "hjddmdk72nd"
        text = f"//thread {test}"

        await webhook.send(text, username="Maev's helper", avatar_url="https://xhost.maev.site/icons/github_logo.png")


# send multiple attachments
async def send_attachments():
    async with aiohttp.ClientSession() as session:
        files = []
        files_dir = "files"
        for file in os.listdir(files_dir):
            files.append(f"{files_dir}/{file}")
        thread_channel_id = 1148973528146776084

        upload_list = [discord.File(file) for file in files]

        webhook = Webhook.from_url(webhook_url, session=session)
        await webhook.send(files=upload_list, username="Maev's helper",
                           avatar_url="https://xhost.maev.site/icons/github_logo.png",
                           thread=discord.Object(thread_channel_id))


# asyncio.run(thread_request())
# asyncio.run(foo())
asyncio.run(send_attachments())
