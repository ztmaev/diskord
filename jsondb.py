import json
import sqlite3

import mysql.connector

username = "maev"
password = "Alph4"
host = "arc.maev.site"
port = "3306"


def connect_to_db_remote(database_name=None):
    if database_name is None:
        db = mysql.connector.connect(
            host=host,
            user=username,
            passwd=password,
            port=port
        )
        return db
    else:
        db = mysql.connector.connect(
            host=host,
            user=username,
            passwd=password,
            port=port,
            database=database_name
        )
        return db


def write_to_db_sqlite(json_data):
    db_name = 'test.db'
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS files
                    (file_id text, file_name text, file_size text, chunks_number integer, chunk_size integer, file_type text, filetype_icon_url text, owner_id integer, files text, thread_info text)''')
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
    thread_info = json.dumps(data['thread_info'])

    # insert
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("INSERT INTO files VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (file_id, file_name, file_size, chunks_number, chunk_size, file_type, filetype_icon_url, owner_id, files, thread_info))
    conn.commit()
    conn.close()


def write_to_db_remote(json_data):
    db_name = 'test'
    # check if database exists
    db = connect_to_db_remote()
    list_of_databases = db.cursor()
    list_of_databases.execute("SHOW DATABASES")

    db_list = []
    for x in list_of_databases:
        db_list.append(x[0])

    # create database if it doesn't exist
    if db_name not in db_list:
        db.cursor().execute("CREATE DATABASE " + db_name)
        db.commit()

    # create table if it doesn't exist
    db = connect_to_db_remote(db_name)
    db.cursor().execute('''CREATE TABLE IF NOT EXISTS files
                        (file_id text, file_name text, file_size text, chunks_number integer, chunk_size integer, file_type text, filetype_icon_url text, owner_id bigint, files text, thread_info text)''')
    db.commit()
    db.close()

    # parse
    data = json_data

    file_id = data['file_id']
    file_name = data['file_name']
    file_size = data['file_size']
    chunks_number = data['chunks_number']
    chunk_size = data['chunk_size']
    file_type = data['file_type']
    filetype_icon_url = data['filetype_icon_url']
    owner_id = int(data['owner_id'])
    files = json.dumps(data['files'])
    thread_info = json.dumps(data['thread_info'])

    # insert
    db = connect_to_db_remote(db_name)
    db.cursor().execute("INSERT INTO files VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (file_id, file_name, file_size, chunks_number, chunk_size, file_type, filetype_icon_url,
                         owner_id, files, thread_info))
    db.commit()
    db.close()


def write_to_db(json_data):
    # write_to_db_sqlite(json_data)
    write_to_db_remote(json_data)
