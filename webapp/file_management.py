import math
import os

import requests


def get_filetype_icon_url(file_type):
    return "https://xhost.maev.site/icons/allin.png"


def convert_file_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"


split_output_folder = "temp/files/out_split"
merge_output_folder = "temp/files/out_merged"


def download_file(url, output_folder, file_name):
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Combine the output folder and file name to create the full path
    file_path = os.path.join(output_folder, file_name)

    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Save the content of the response to the file
        with open(file_path, 'wb') as file:
            file.write(response.content)

        # print(f"Downloaded {file_name} to {output_folder}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading {file_name}: {e}")


# split
def split_file(input_file, chunk_size_mb):
    file_name = input_file.split('/')[-1]
    file_type = input_file.split('/')[-1].split('.')[-1]
    file_size = convert_file_size(os.path.getsize(input_file))
    bytes_size = chunk_size_mb * 1024 * 1024
    filetype_icon_url = get_filetype_icon_url(file_type)
    split_files = []
    try:
        with open(input_file, 'rb') as f:
            index = 0
            while True:
                chunk = f.read(bytes_size)
                if not chunk:
                    break

                output_file = os.path.join(split_output_folder, f"{file_name}_{index + 1}.bin")

                with open(output_file, 'wb') as out_f:
                    out_f.write(chunk)

                index += 1
                split_files.append(output_file)
    except Exception as e:
        print(e)
        return

    chunks_number = len(split_files)

    # create json with file info
    file_info = {
        'file_name': file_name,
        'file_type': file_type,
        'file_size': file_size,
        'chunk_size': chunk_size_mb,
        'chunks_number': chunks_number,
        'chunks': split_files,
        'filetype_icon_url': filetype_icon_url
    }
    # return the json
    return file_info


# merge
def merge_files(file_info_json):
    original_file_name = file_info_json['file_name']
    files = file_info_json['files']
    file_id = file_info_json['file_id']

    output_dir_name = file_id

    # create output folder
    output_folder = os.path.join(merge_output_folder, output_dir_name)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # download files
    file_names = []
    for file in files:
        file_name = file['file_name']
        file_url = file['file_url']
        file_names.append(file_name)

        # download file
        download_file(file_url, output_folder, file_name)

    # merge files
    output_file_path = f"{merge_output_folder}/{file_id}/{original_file_name}"

    try:
        with open(output_file_path, 'wb') as output_file:
            for chunk_file in file_names:
                chunk_file = f"{merge_output_folder}/{file_id}/{chunk_file}"
                with open((chunk_file), 'rb') as chunk:
                    output_file.write(chunk.read())

        # delete chunks
        for chunk_file in file_names:
            chunk_file = f"{merge_output_folder}/{file_id}/{chunk_file}"
            os.remove(chunk_file)

        return output_file_path


    except Exception as e:
        print(e)
        return

