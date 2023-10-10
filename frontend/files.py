import asyncio
import json
import math
import os
from datetime import datetime

import aiohttp
import discord
import mysql.connector
import pytz
import websockets
from discord import Webhook

from config import webhook_url, webhook_name, webhook_avatar_url

uploads_dir = 'files/media'
split_output_dir = f"files/split_output"
chunk_size_mb = 5


def current_time():
    gmt_plus_3 = pytz.timezone('Etc/GMT-3')
    current_time = datetime.now(gmt_plus_3)
    return current_time


def get_db():
    db = mysql.connector.connect(
        host="arc.maev.site",
        user="maev",
        passwd="Alph4",
        port="3306",
        database="Alpha1",
        charset="utf8mb4",
    )
    return db


def convert_file_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"


def split_file(file, chunk_size_mb):
    split_files = []
    file_name = file
    file_path = os.path.join(f"{uploads_dir}/{file}")
    output_dir = f"{split_output_dir}/{file[:18]}"
    os.makedirs(output_dir, exist_ok=True)

    bytes_size = chunk_size_mb * 1024 * 1024

    try:
        with open(file_path, 'rb') as f:
            index = 0
            while True:
                chunk = f.read(bytes_size)
                if not chunk:
                    break

                output_file_name = f"{file_name}_{index + 1}.bin"
                output_file = os.path.join(f"{output_dir}/{output_file_name}")

                with open(output_file, 'wb') as out_f:
                    out_f.write(chunk)

                index += 1
                split_files.append(output_file_name)
        return split_files
    except Exception as e:
        print(e)
        return None


def process_upload_url(url, session_id):
    # TODO: url download
    pass


def process_upload_files(files, session_id):
    try:
        for file in files:
            original_filename = file[19:]
            files_directory = file[:18]
            file_type = original_filename.split('.')[-1]
            filesize = os.path.getsize(f"{uploads_dir}/{file}")
            filesize_simple = convert_file_size(filesize)
            file_list = split_file(file, chunk_size_mb)
            chunks_number = len(file_list)
            # print(file_list)
            chunks_size = chunk_size_mb
            owner_id = session_id

            # write to db
            db = get_db()
            cursor = db.cursor()
            cursor.execute("""
                INSERT INTO files (
                    file_name,
                    file_id,
                    file_type,
                    file_size,
                    file_size_simple,
                    chunks_number,
                    chunks_size,
                    files_directory,
                    owner_id,
                    date_created,
                    date_updated
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
                )
            """, (
                original_filename,
                files_directory,
                file_type,
                filesize,
                filesize_simple,
                chunks_number,
                chunks_size,
                files_directory,
                owner_id,
            ))
            db.commit()
            file_id = cursor.lastrowid
            for subfile in file_list:
                chunk_file_id = subfile.split('_')[-1].split('.')[0]

                cursor.execute("""
                    INSERT INTO subfiles (
                        main_file_id,
                        chunk_file_id,
                        file_name,
                        date_created
                    ) VALUES (
                        %s, %s, %s, NOW()
                    )
                """, (
                    file_id,
                    chunk_file_id,
                    subfile,
                ))
                db.commit()
            # upload files
            file_unique_id = files_directory
            file_type_icon_url = "https://xhost.maev.site/icons/allin.png"
            file_info = {"file_name": file, "file_type": file_type, "size": filesize, "chunks_number": chunks_number,
                         "chunk_size": chunk_size_mb, "owner_id": owner_id, "file_unique_id": file_unique_id,
                         "files": file_list, "filetype_icon_url": file_type_icon_url}
            upload_files(file_info)


    except Exception as e:
        print(e)
        return None


# webhook url
def get_webhook_url():
    return webhook_url


async def fetch_thread_info(query):
    uri = "ws://arc.maev.site:8765"
    try:
        async with websockets.connect(uri) as websocket:
            await websocket.send(query)

            websocket_feedback = await websocket.recv()
            if websocket_feedback:
                thread_info = json.loads(websocket_feedback)
                return thread_info
            else:
                return False
    except Exception as e:
        return False


def get_thread_info(thread_name):
    query = f"get_thread_info_%_{thread_name}"
    # get thread info until a valid response is received
    while True:
        thread_info = asyncio.run(fetch_thread_info(query))
        if thread_info and thread_info["thread_id"]:
            break
    return thread_info


# thread creation
async def create_thread(thread_name):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(get_webhook_url(), session=session)
        message_content = f"//thread {thread_name}"

        message = await webhook.send(message_content, username=webhook_name,
                                     avatar_url=webhook_avatar_url, wait=True)
        thread_id = message.id
        return thread_id


# edit the previous message (create thread)
async def send_banner_embed(file_info_full, is_thread=False, message_id=None):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(get_webhook_url(), session=session)
        embed = discord.Embed(colour=discord.Color.purple(), title="📁 File uploaded", timestamp=current_time(),
                              description=f"""
                        **Filename:** `{file_info_full['file_name']}`
                        **Id:** `{file_info_full['file_id']}`
                        **Filetype:** `{file_info_full['file_type']}`
                        **Filesize:** `{file_info_full['file_size']}`
                        **Chunks:** `{file_info_full['chunks_number']}`
                        **Chunk size:** `{file_info_full['chunk_size']}`
                        """)
        # embed.set_image(url=file_info_full['file_thumbnail_url'])
        embed.set_thumbnail(url=file_info_full['filetype_icon_url'])
        embed.url = file_info_full['thread_url']

        if is_thread:
            await webhook.send(embed=embed, username=webhook_name,
                               avatar_url=webhook_avatar_url, thread=discord.Object(file_info_full['thread_id']))
        else:
            await webhook.edit_message(message_id=message_id, embed=embed, content=None)


async def send_json_metadata(file_info_full):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(get_webhook_url(), session=session)
        # create json metadata
        json_metadata = {
            "file_name": file_info_full['file_name'],
            "file_id": file_info_full['file_id'],
            "file_type": file_info_full['file_type'],
            "file_size": file_info_full['file_size'],
            "chunks_number": int(file_info_full['chunks_number']),
            "chunk_size": file_info_full['chunk_size'],
            "filetype_icon_url": file_info_full['filetype_icon_url'],
            "files": file_info_full['files'],
            "owner_id": file_info_full['owner_id'],
        }
        with open(f"files/metadata/{file_info_full['file_id']}.json", "w") as f:
            json.dump(json_metadata, f, indent=4)

        await webhook.send(file=discord.File(f"files/metadata/{file_info_full['file_id']}.json"), username=webhook_name,
                           avatar_url=webhook_avatar_url,
                           thread=discord.Object(file_info_full['thread_id']))
        # delete json file
        os.remove(f"files/metadata/{file_info_full['file_id']}.json")


async def send_attachments(files, thread_id):
    # upload each file
    for file in files:
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(get_webhook_url(), session=session)
            await webhook.send(file=discord.File(f"files/split_output/{file[:18]}/{file}"), username=webhook_name,
                               avatar_url=webhook_avatar_url,
                               thread=discord.Object(thread_id))


async def send_end_message(thread_id):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(get_webhook_url(), session=session)
        await webhook.send("//end", username=webhook_name,
                           avatar_url=webhook_avatar_url,
                           thread=discord.Object(thread_id))


def upload_files(file_info):
    # create thread
    thread_name = file_info['file_unique_id']
    thread_message_id = asyncio.run(create_thread(thread_name))
    # print(thread_message_id)
    if thread_message_id:
        while True:
            thread_info = get_thread_info(thread_name)
            # print(thread_info)
            if thread_info and thread_info["thread_id"]:
                break

        thread_url = thread_info["thread_url"]
        file_id = thread_name
        file_thumbnail_url = "https://xhost.maev.site/icons/diskord.png"

        file_info_full = {
            "file_name": file_info['file_name'],
            "file_id": file_id,
            "file_type": file_info['file_type'],
            "file_size": file_info['size'],
            "chunks_number": file_info['chunks_number'],
            "chunk_size": file_info['chunk_size'],
            "filetype_icon_url": file_info['filetype_icon_url'],
            "thread_id": thread_info["thread_id"],
            "thread_url": thread_url,
            "file_thumbnail_url": file_thumbnail_url,
            "files": file_info['files'],
            "owner_id": file_info['owner_id'],
        }

        # edit the previous message (create thread)
        asyncio.run(send_banner_embed(file_info_full, is_thread=True))

        # banner
        asyncio.run(send_banner_embed(file_info_full, message_id=thread_message_id))

        # send json metadata
        asyncio.run(send_json_metadata(file_info_full))

        # send files
        asyncio.run(send_attachments(file_info_full['files'], thread_info["thread_id"]))

        # delete files
        for file in file_info_full['files']:
            os.remove(f"files/split_output/{file[:18]}/{file}")

        # send end message
        asyncio.run(send_end_message(file_info_full['thread_id']))

        # update db
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            UPDATE files SET
                file_type_icon_url = %s,
                thread_id = %s,
                thread_url = %s,
            # update database
            # filetype_icon_url, 
                date_updated = NOW()
            WHERE file_id = %s
        """, (
            file_thumbnail_url,
            thread_info["thread_id"],
            thread_url,
            file_id,
        ))
        db.commit()

        return True

# TODO: Upload queue + webhook integration

def update_file():
    pass

