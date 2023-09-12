import asyncio
import sys

import requests

from file_management import split_file
from webhook_manager import *

chunk_size_mb = 20


def master_is_file(filename, temp_uuid):
    # print(filename)
    # check if file exists
    original_filename = filename.split(f"{temp_uuid}_", 1)[1]

    if os.path.exists(f"temp/files/media/{filename}"):
        # split file
        split_file_data = split_file(f"temp/files/media/{filename}", chunk_size_mb)

        # parse
        # file_name = split_file_data['file_name']
        file_name = original_filename
        file_type = split_file_data['file_type']
        file_size = split_file_data['file_size']
        chunk_size = split_file_data['chunk_size']
        chunks_number = split_file_data['chunks_number']
        chunks = split_file_data['chunks']
        filetype_icon_url = split_file_data['filetype_icon_url']

        # create thread
        thread_uuid = generate_thread_id()
        thread_message_id = asyncio.run(create_thread(thread_uuid))

        # get thread info
        while True:
            thread_info = get_thread_info(thread_uuid)
            if thread_info:
                break

        # send banner
        thread_id = thread_info["thread_id"]
        thread_url = thread_info["thread_url"]
        file_id = thread_uuid
        file_thumbnail_url = "https://xhost.maev.site/icons/github_logo.png"

        # thread
        asyncio.run(
            send_banner_embed(thread_url, thread_id, file_name, file_id, file_type, file_size, chunks_number,
                              chunk_size, file_thumbnail_url,
                              filetype_icon_url, is_thread=True))

        # banner
        asyncio.run(send_banner_embed(thread_url, thread_id, file_name, file_id, file_type, file_size, chunks_number,
                                      chunk_size, file_thumbnail_url,
                                      filetype_icon_url, message_id=thread_message_id))

        # json metadata
        content = {
            "file_name": file_name,
            "file_id": file_id,
            "file_type": file_type,
            "file_size": file_size,
            "chunks_number": chunks_number,
            "chunk_size": chunk_size,
            "filetype_icon_url": filetype_icon_url,
            "files": chunks
        }
        asyncio.run(send_json_metadata(thread_id, file_id, content))

        # files
        file_upload_check = asyncio.run(send_attachments(chunks, thread_id))

        # delete file if uploaded
        if file_upload_check:
            os.remove(f"temp/files/media/{filename}")

        # delete chunks
        # for chunk in chunks:
        #     os.remove(chunk)

        # create master json
        master_json = {
            "file_name": file_name,
            "file_id": file_id,
            "file_type": file_type,
            "file_size": file_size,
            "chunks_number": chunks_number,
            "chunk_size": chunk_size,
            "filetype_icon_url": filetype_icon_url,
            "thread_id": thread_id,
            "thread_url": thread_url,
            "files": chunks
        }

        if not os.path.exists("db_dir"):
            os.makedirs("db_dir")

        with open(f"db_dir/{file_id}.json", "w") as f:
            json.dump(master_json, f, indent=4)


def master_is_url(filename, temp_uuid):
    url = filename
    save_path = f"temp/files/media/{temp_uuid}_{url.split('/')[-1]}"
    while True:
        if os.path.exists(save_path):
            break
        else:
            try:
                response = requests.get(url, stream=True)
                response.raise_for_status()

                with open(save_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)

                # print(f"Downloaded {url} to {save_path}")

            except requests.exceptions.RequestException as e:
                # print(f"Error downloading {url}: {e}")
                return

    filename = f"{temp_uuid}_{url.split('/')[-1]}"
    # print(filename)

    # check if file exists
    original_filename = filename.split(f"{temp_uuid}_", 1)[1]

    if os.path.exists(f"temp/files/media/{filename}"):
        # print("File exists")
        # split file
        split_file_data = split_file(f"temp/files/media/{filename}", chunk_size_mb)
        # print("Split file")
        # parse
        # file_name = split_file_data['file_name']
        file_name = original_filename
        file_type = split_file_data['file_type']
        file_size = split_file_data['file_size']
        chunk_size = split_file_data['chunk_size']
        chunks_number = split_file_data['chunks_number']
        chunks = split_file_data['chunks']
        filetype_icon_url = split_file_data['filetype_icon_url']

        # create thread
        thread_uuid = generate_thread_id()
        thread_message_id = asyncio.run(create_thread(thread_uuid))

        # get thread info
        while True:
            thread_info = get_thread_info(thread_uuid)
            if thread_info:
                break

        # send banner
        thread_id = thread_info["thread_id"]
        thread_url = thread_info["thread_url"]
        file_id = thread_uuid
        file_thumbnail_url = "https://xhost.maev.site/icons/github_logo.png"

        # thread
        asyncio.run(
            send_banner_embed(thread_url, thread_id, file_name, file_id, file_type, file_size, chunks_number,
                              chunk_size, file_thumbnail_url,
                              filetype_icon_url, is_thread=True))

        # banner
        asyncio.run(send_banner_embed(thread_url, thread_id, file_name, file_id, file_type, file_size, chunks_number,
                                      chunk_size, file_thumbnail_url,
                                      filetype_icon_url, message_id=thread_message_id))

        # json metadata
        content = {
            "file_name": file_name,
            "file_id": file_id,
            "file_type": file_type,
            "file_size": file_size,
            "chunks_number": chunks_number,
            "chunk_size": chunk_size,
            "filetype_icon_url": filetype_icon_url,
            "files": chunks
        }
        # print("Sending json metadata")
        asyncio.run(send_json_metadata(thread_id, file_id, content))

        # print("Sending attachments")
        # files
        file_upload_check = asyncio.run(send_attachments(chunks, thread_id))

        # delete file if uploaded
        if file_upload_check:
            os.remove(f"temp/files/media/{filename}")

        # create master json
        master_json = {
            "file_name": file_name,
            "file_id": file_id,
            "file_type": file_type,
            "file_size": file_size,
            "chunks_number": chunks_number,
            "chunk_size": chunk_size,
            "filetype_icon_url": filetype_icon_url,
            "thread_id": thread_id,
            "thread_url": thread_url,
            "files": chunks
        }

        if not os.path.exists("db_dir"):
            os.makedirs("db_dir")

        with open(f"db_dir/{file_id}.json", "w") as f:
            json.dump(master_json, f, indent=4)

        # send end mmessage
        asyncio.run(send_end_message(thread_id))



# master function
def master(filename, temp_uuid, is_url=False):
    # print("Master")
    if is_url:
        # print("URL")
        master_is_url(filename, temp_uuid)
        # threading.Thread(target=master_is_url, args=(filename, temp_uuid)).start()
    else:
        # print("File")
        master_is_file(filename, temp_uuid)
        # threading.Thread(target=master_is_file, args=(filename, temp_uuid)).start()
        # master_is_url(filename, temp_uuid)


# executor
# get args
filename = sys.argv[1]
temp_uuid = sys.argv[2]
file_url = sys.argv[3]
if file_url == "url":
    is_url = True
else:
    is_url = False

# run master
# print(f"Running master:{filename},{temp_uuid},{is_url}")
master(filename, temp_uuid, is_url=is_url)

# Running master:https://xhost.maev.site/resized/atafp.jpg,58cf91c6-f4bf-4798-94df-6a226d0b9526, True
# Running master:https://xhost.maev.site/resized/atafp.jpg,test1,    True

# executor
# filename = "https://xhost.maev.site/resized/atafp.jpg"
# temp_uuid = "58cf91c6-f4bf-4798-94df-6a226d0b9526"
# file_url = "url"
# if file_url == "url":
#     is_url = True
#     print("URL")
# else:
#     is_url = False
#     print("File")
#
# # run master
# print(f"Running master:{filename},{temp_uuid},{is_url}")
# master(filename, temp_uuid, is_url=True)
