import json
import uuid
from datetime import datetime

import aiohttp
import discord
import pytz
from discord import Webhook

with open("../../config.json") as f:
    config = json.load(f)
webhook_avatar_url = config["webhook_avatar_url"]


def current_time():
    gmt_plus_3 = pytz.timezone('Etc/GMT-3')
    current_time = datetime.now(gmt_plus_3)
    return current_time


def get_webhook_url():
    with open("../../config.json") as f:
        config = json.load(f)
    webhook_url = config["webhook_url"]
    return webhook_url


def fetch_ids_config():
    with open("../../ids_config.json") as f:
        ids_config = json.load(f)
    return ids_config


def get_thread_info(thread_name):
    try:
        ids_config = fetch_ids_config()
        for entry in ids_config:
            if entry["thread_name"] == thread_name:
                return entry
    except Exception as e:
        pass


def generate_thread_id():
    # using uuid4
    return str(uuid.uuid4())


# thread creation
async def create_thread(thread_uuid):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(get_webhook_url(), session=session)
        message_content = f"//thread {thread_uuid}"

        thread_request_message = await webhook.send(message_content, username="Maev's helper",
                                                    avatar_url="https://xhost.maev.site/icons/github_logo.png")


# Banner
async def send_banner_embed(thread_url, thread_id, is_thread, file_name, file_id, file_type, file_size, chunks_number, chunk_size, file_thumbnail_url,
                            filetype_image_url):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(get_webhook_url(), session=session)
        embed = discord.Embed(colour=discord.Color.purple(), title="📁 File uploaded", timestamp=current_time(),
                              description=f"""
                        Filename: `{file_name}`
                        Id: `{file_id}`
                        Filetype: `{file_type}`
                        Filesize: `{file_size}`
                        Chunks: `{chunks_number}`
                        Chunk size: `{chunk_size}`
                        """)
        embed.set_image(url=file_thumbnail_url)
        embed.set_thumbnail(url=filetype_image_url)
        embed.url = thread_url

        if is_thread:
            await webhook.send(embed=embed, username="Maev's helper",
                           avatar_url=webhook_avatar_url, thread=discord.Object(thread_id))
        else:
            await webhook.send(embed=embed, username="Maev's helper",
                           avatar_url=webhook_avatar_url)


# Aattachments
async def send_attachments(files, thread_id):
    async with aiohttp.ClientSession() as session:

        upload_list = [discord.File(file) for file in files]

        webhook = Webhook.from_url(get_webhook_url(), session=session)
        await webhook.send(files=upload_list, username="Maev's helper",
                           avatar_url="https://xhost.maev.site/icons/github_logo.png",
                           thread=discord.Object(thread_id))

# aysnc json metadata
async def send_json_metadata(thread_id, content):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(get_webhook_url(), session=session)
        # create json file in metadata folder
        with open(f"metadata/{thread_id}.json", "w") as f:
            json.dump(content, f, indent=4)
        # send json file
        await webhook.send(file=discord.File(f"metadata/{thread_id}.json"), username="Maev's helper",
                           avatar_url="https://xhost.maev.site/icons/github_logo.png",
                           thread=discord.Object(thread_id))


# Tests
# asyncio.run(thread_request())
# asyncio.run(send_banner_embed("jdhdj.png", "636hdb3b2", "zip", "123.74 mbs", "74", "1.67 mbs",
#                               "https://media.discordapp.net/attachments/1148598158721564834/1148598159858208818/Screenshot_2023-09-05_153451.jpg?width=664&height=341",
#                               "https://xhost.maev.site/icons/github_logo.png"))
# asyncio.run(send_attachments())

# print(fetch_ids_config())
# print(get_thread_info("c386c4db-4b31-4ba6-8ad7-7d6960bef015"))