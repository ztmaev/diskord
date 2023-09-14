import asyncio
import os
import threading

from dep_tests import *
from files import split_file

chunk_size_mb = 1

def master_function(filename, temp_uuid):
    # check if file exists
    original_filename = filename.split(f"{temp_uuid}_", 1)[1]

    if os.path.exists(f"files/media/{filename}"):
        # split file
        split_file_data = split_file(f"files/media/{filename}", chunk_size_mb)

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
            os.remove(f"files/media/{filename}")

        # delete chunks
        for chunk in chunks:
            os.remove(chunk)


# master function
def master(filename, temp_uuid):
    threading.Thread(target=master_function, args=(filename, temp_uuid)).start()
