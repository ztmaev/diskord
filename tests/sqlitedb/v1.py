import sqlite3
import requests
import json

db_name = 'test.db'

# sample data
data_str = '''
{
    "chunk_size": 20,
    "chunks_number": 1,
    "file_id": "2964e8ed-6eab-427f-bda4-b14f26e665f1",
    "file_name": "atafp.jpg",
    "file_size": "6.92 KB",
    "file_type": "jpg",
    "files": [
        {
            "file_name": "2964e8ed-6eab-427f-bda4-b14f26e665f1.json",
            "file_url": "https://cdn.discordapp.com/attachments/1151083790568013894/1151083794179305573/2964e8ed-6eab-427f-bda4-b14f26e665f1.json"
        },
        {
            "file_name": "303f19ab-77c4-4b71_atafp.jpg_1.bin",
            "file_url": "https://cdn.discordapp.com/attachments/1151083790568013894/1151083795718623234/303f19ab-77c4-4b71_atafp.jpg_1.bin"
        }
    ],
    "filetype_icon_url": "https://xhost.maev.site/icons/allin.png",
    "owner_id": 12345678
}
'''

def write_to_db(json_data):
    # create db if not exists
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS files
                    (file_id text, file_name text, file_size text, chunks_number integer, chunk_size integer, file_type text, filetype_icon_url text, owner_id integer, files text)''')
    conn.commit()
    conn.close()

    # parse
    # load json_data
    data = json_data

    file_id = data['file_id']
    file_name = data['file_name']
    file_size = data['file_size']
    chunks_number = data['chunks_number']
    chunk_size = data['chunk_size']
    file_type = data['file_type']
    filetype_icon_url = data['filetype_icon_url']
    owner_id = data['owner_id']
    files = json.dumps(data['files'])

    # insert
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("INSERT INTO files VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (file_id, file_name, file_size, chunks_number, chunk_size, file_type, filetype_icon_url, owner_id, files))
    conn.commit()
    conn.close()

    return True

# execute
# write_to_db(data_str)
