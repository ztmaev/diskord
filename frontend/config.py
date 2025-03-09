import asyncio
import json
from urllib import parse

import mysql.connector
import websockets

uri = "ws://...:8765"
config_password = "password"
# db_name = "dirs_v1"
db_name = "maev"
# db_host = "arc.maev.site"
db_host = "127.0.0.1"

async def get_config():
    try:
        async with websockets.connect(uri) as websocket:
            query = f"get_config_%_{config_password}"
            await websocket.send(query)

            websocket_feedback = await websocket.recv()
            if websocket_feedback:
                config = json.loads(websocket_feedback)
                return config
            else:
                return False
    except Exception as e:
        print(e)
        return False


# load config
config = asyncio.run(get_config())
if config:
    print("Fetched config")
else:
    print("Failed to fetch config")
    exit()

diskord_channel_id = config["diskord_channel_id"]
webhook_name = config["webhook_name"]
webhook_avatar_url = config["webhook_avatar_url"]
webhook_url = config["webhook_url"]
token = config["token"]

client_id = ""
client_secret = ""
redirect_uri = "http://localhost:4321/oauth/callback"
oauth_url = ""

admin_ids = []


def get_db():
    db = mysql.connector.connect(
        host=db_host,
        user="",
        passwd="",
        port="3306",
        database=db_name,
        charset="utf8mb4",
    )
    return db
