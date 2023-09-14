import json
import os
import uuid
from datetime import datetime
import websockets
from config import uri, webhook_avatar_url, webhook_url

import aiohttp
import discord
import pytz
from discord import Webhook


#load config
async def get_thread_info(thread_uuid):
    try:
        async with websockets.connect(uri) as websocket:
            thread_name = thread_uuid
            query = f"get_config_%_{thread_name}"
            await websocket.send(query)

            websocket_feedback = await websocket.recv()
            if websocket_feedback:
                thread_info = json.loads(websocket_feedback)
                return thread_info
            else:
                return False
    except Exception as e:
        # print(e)
        return False



def current_time():
    gmt_plus_3 = pytz.timezone('Etc/GMT-3')
    current_time = datetime.now(gmt_plus_3)
    return current_time


def get_webhook_url():
    return webhook_url


def fetch_ids_config():
    with open("temp/ids_config.json") as f:
        ids_config = json.load(f)
    # delete file
    # os.remove("temp/ids_config.json")
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
    # queue system for uploading files
    queue = []
    queue_file = "temp/queue.json"
    if os.path.exists(queue_file):
        # add thread id to bottom of queue
        with open(queue_file) as f:
            queue = json.load(f)
        queue.append(thread_id)
        with open(queue_file, "w") as f:
            json.dump(queue, f)

        ##########################################

    else:
        # create file and add empty list then add the thread id
        with open(queue_file, "w") as f:
            json.dump([], f)
        queue.append(thread_id)

        # add thread id to bottom of queue
        with open(queue_file) as f:
            queue = json.load(f)
        queue.append(thread_id)
        with open(queue_file, "w") as f:
            json.dump(queue, f)

        ##########################################

    # check if thread id is first in queue
    # loop until thread id is first in queue and processed
    while True:
        try:
            with open(queue_file) as f:
                queue = json.load(f)
        except Exception as e:
            print(e)
            pass
        if queue[0] == thread_id:
            # print(files)
            #
            for file in files:
                async with aiohttp.ClientSession() as session:
                    webhook = Webhook.from_url(get_webhook_url(), session=session)
                    await webhook.send(file=discord.File(file), username="Maev's helper",
                                       avatar_url="https://xhost.maev.site/icons/github_logo.png",
                                       thread=discord.Object(thread_id))
                    # delete file
                    os.remove(file)
            # delete thread id from queue
            with open(queue_file) as f:
                queue = json.load(f)
            queue.pop(0)
            with open(queue_file, "w") as f:
                json.dump(queue, f)
            return True

        else:
            continue


# aysnc json metadata
async def send_json_metadata(thread_id, file_id, content):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(get_webhook_url(), session=session)
        # create json file in metadata folder
        with open(f"temp/metadata/{file_id}.json", "w") as f:
            json.dump(content, f, indent=4)
        # send json file
        await webhook.send(file=discord.File(f"temp/metadata/{file_id}.json"), username="Maev's helper",
                           avatar_url="https://xhost.maev.site/icons/github_logo.png",
                           thread=discord.Object(thread_id))
        # delete json file
        os.remove(f"temp/metadata/{file_id}.json")


# end message to thread
async def send_end_message(thread_id):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(get_webhook_url(), session=session)
        await webhook.send("//end", username="Maev's helper",
                           avatar_url="https://xhost.maev.site/icons/github_logo.png",
                           thread=discord.Object(thread_id))
