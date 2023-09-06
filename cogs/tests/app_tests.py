import asyncio
import os

from dep_tests import *

# files
files = []
files_dir = "files"
for file in os.listdir(files_dir):
    files.append(f"{files_dir}/{file}")

# create thread
thread_uuid = generate_thread_id()
asyncio.run(create_thread(thread_uuid))

# get thread info
while True:
    thread_info = get_thread_info(thread_uuid)
    if thread_info:
        break

# send files
thread_id = thread_info["thread_id"]
thread_url = thread_info["thread_url"]
asyncio.run(send_attachments(files, thread_id))

# send banner
thread_url = thread_info["thread_url"]
file_name = "jdhdj.png"
file_id = thread_uuid
file_type = "zip"
file_size = "123.74 mbs"
chunks_number = len(files)
chunk_size = "1.67 mbs"
file_thumbnail_url = "https://media.discordapp.net/attachments/1148598158721564834/1148598159858208818/Screenshot_2023-09-05_153451.jpg?width=664&height=341"
filetype_image_url = "https://xhost.maev.site/icons/github_logo.png"
asyncio.run(send_banner_embed(thread_url, file_name, file_id, file_type, file_size, chunks_number, chunk_size, file_thumbnail_url,
                                filetype_image_url))
