import math
import os

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
