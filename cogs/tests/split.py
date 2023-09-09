import os
import json
import uuid
import math

def generate_uuid():
    return str(uuid.uuid4())[:13]

def convert_file_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

def split_file(input_file, output_folder, json_folder, chunk_size_mb):
    chunk_size = chunk_size_mb * 1024 * 1024
    plain_name = (input_file.split('/')[-1]).split('.')[0]
    out_name = f"{plain_name}_{generate_uuid()}"
    original_name = input_file.split('/')[-1]
    file_extension = input_file.split('/')[-1].split('.')[-1]
    split_files = []
    try:
        with open(input_file, 'rb') as f:
            index = 0
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break

                output_file = os.path.join(output_folder, f"{out_name}_{index + 1}.bin")

                with open(output_file, 'wb') as out_f:
                    out_f.write(chunk)

                index += 1
                split_files.append(output_file)
    except Exception as e:
        print(e)
        return
    # create json with file info
    file_info = {
        'file_name': out_name,
        'original_name': original_name,
        'file_extension': file_extension,
        'file_size': convert_file_size(os.path.getsize(input_file)),
        'chunk_size': chunk_size,
        'chunks': split_files
    }
    json_file = os.path.join(json_folder, f"{out_name}.json")
    with open(json_file, 'w') as f:
        json.dump(file_info, f, indent=4)

    return json_file


if __name__ == "__main__":
    input_file_path = "files/media/2.txt"
    output_folder_path = "files/out_split"
    json_folder = "files/json_data"
    chunk_size_mb = 1

    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)

    print(split_file(input_file_path, output_folder_path, json_folder, chunk_size_mb))

    print("File splitting completed.")
