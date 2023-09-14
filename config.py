import asyncio
import json
from urllib import parse

import websockets

uri = "ws://arc.maev.site:8765"
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

token = "MTE0MTAwMDg0MzA3MjY0NzI5MA.G1jGag.htRqZBklgFzeIZI1Ka6xhcRLTW77OtEzN7e1VQ"
client_id = 1141000843072647290
client_secret = "QWVGp6-duEfKk51-cX_fal2Z_EL1GDez"
redirect_uri = "http://localhost:5000/oauth/callback"
oauth_url = f"https://discord.com/api/oauth2/authorize?client_id=1141000843072647290&redirect_uri={parse.quote(redirect_uri)}&response_type=code&scope=identify"
