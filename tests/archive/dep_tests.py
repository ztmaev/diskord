import json
import os
import uuid
from datetime import datetime

import aiohttp
import discord
import pytz
from discord import Webhook

with open("../../bot/config.json") as f:
    config = json.load(f)
webhook_avatar_url = config["webhook_avatar_url"]


def current_time():
    gmt_plus_3 = pytz.timezone('Etc/GMT-3')
    current_time = datetime.now(gmt_plus_3)
    return current_time


def get_webhook_url():
    with open("../../bot/config.json") as f:
        config = json.load(f)
    webhook_url = config["webhook_url"]
    return webhook_url


def fetch_ids_config():
    with open("../../temp/ids_config.json") as f:
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

        message = await webhook.send(message_content, username="Maev's helper",
                                     avatar_url="https://xhost.maev.site/icons/github_logo.png", wait=True)
        # print(message.id)
        return message.id


# Banner
# edit the previous message (create thread)]
async def send_banner_embed(thread_url, thread_id, file_name, file_id, file_type, file_size, chunks_number, chunk_size,
                            file_thumbnail_url,
                            filetype_icon_url, is_thread=False, message_id=None):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(get_webhook_url(), session=session)
        embed = discord.Embed(colour=discord.Color.purple(), title="📁 File uploaded", timestamp=current_time(),
                              description=f"""
                        **Filename:** `{file_name}`
                        **Id:** `{file_id}`
                        **Filetype:** `{file_type}`
                        **Filesize:** `{file_size}`
                        **Chunks:** `{chunks_number}`
                        **Chunk size:** `{chunk_size}`
                        """)
        # embed.set_image(url=file_thumbnail_url)
        embed.set_thumbnail(url=filetype_icon_url)
        embed.url = thread_url

        if is_thread:
            await webhook.send(embed=embed, username="Maev's helper",
                               avatar_url=webhook_avatar_url, thread=discord.Object(thread_id))
        else:
            await webhook.edit_message(message_id=message_id, embed=embed, content=None)


# Aattachments
async def send_attachments(files, thread_id):
    async with aiohttp.ClientSession() as session:
        for file in files:
            webhook = Webhook.from_url(get_webhook_url(), session=session)
            await webhook.send(file=discord.File(file), username="Maev's helper",
                               avatar_url="https://xhost.maev.site/icons/github_logo.png",
                               thread=discord.Object(thread_id))

        return True


# aysnc json metadata
async def send_json_metadata(thread_id, file_id, content):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(get_webhook_url(), session=session)
        # create json file in metadata folder
        with open(f"metadata/{file_id}.json", "w") as f:
            json.dump(content, f, indent=4)
        # send json file
        await webhook.send(file=discord.File(f"metadata/{file_id}.json"), username="Maev's helper",
                           avatar_url="https://xhost.maev.site/icons/github_logo.png",
                           thread=discord.Object(thread_id))
        # delete json file
        os.remove(f"metadata/{file_id}.json")


# end message to thread
async def send_end_message(thread_id):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(get_webhook_url(), session=session)
        await webhook.send("//end", username="Maev's helper",
                           avatar_url="https://xhost.maev.site/icons/github_logo.png",
                           thread=discord.Object(thread_id))
