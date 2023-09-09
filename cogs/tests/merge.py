import os
import json

def merge_chunks(json_file_path, output_folder):
    try:
        with open(json_file_path, 'r') as json_file:
            file_info = json.load(json_file)
    except Exception as e:
        print(e)
        return

    file_name = file_info['file_name']
    original_name = file_info['original_name']
    file_extension = file_info['file_extension']
    chunk_size = file_info['chunk_size']
    chunks = file_info['chunks']

    output_file_path = os.path.join(output_folder, original_name)

    try:
        with open(output_file_path, 'wb') as output_file:
            for chunk_file in chunks:
                with open(chunk_file, 'rb') as chunk:
                    output_file.write(chunk.read())
    except Exception as e:
        print(e)
        return

    print("File merging completed.")


if __name__ == "__main__":
    json_file_path = "files/json_data/Apkpure_8ea13d12-9f78.json"
    output_folder = "files/out_merged"

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    merge_chunks(json_file_path, output_folder)
