import asyncio
import json
from urllib import parse

import websockets

uri = "ws:/...:8765"
config_password = "password"


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
# print(config)

diskord_channel_id = config["diskord_channel_id"]
webhook_name = config["webhook_name"]
webhook_avatar_url = config["webhook_avatar_url"]
webhook_url = config["webhook_url"]

token = ""
client_id = ""
client_secret = ""
redirect_uri = ""
oauth_url = ""
