import json
import sqlite3

db_name = 'test.db'


def write_to_db(json_data):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS files
                    (file_id text, file_name text, file_size text, chunks_number integer, chunk_size integer, file_type text, filetype_icon_url text, owner_id integer, files text)''')
    conn.commit()
    conn.close()

    # parse
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
    c.execute("INSERT INTO files VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (file_id, file_name, file_size, chunks_number, chunk_size, file_type, filetype_icon_url, owner_id, files))
    conn.commit()
    conn.close()