import asyncio
import json

import websockets

thread_info_json_path = "temp/ids_config.json"
config_password = "password"
port = 8765
host = "0.0.0.0"


async def diskord(websocket):
    query = await websocket.recv()
    print(f"Received: {query}")
    # split query at _%_ into a and b
    query_ask = query.split("_%_")[0]

    # validation
    if query_ask == "get_thread_info":
        thread_name = query.split("_%_")[1]
        # read json
        try:
            with open(thread_info_json_path) as f:
                thread_info_json = json.load(f)
            # get thread info
            thread_info = {}
            for entry in thread_info_json:
                if entry["thread_name"] == thread_name:
                    thread_info = entry
                    break
            # send thread info
            if thread_info != {}:
                await websocket.send(json.dumps(thread_info))
            else:
                await websocket.send("Thread not found")
        except Exception as e:
            print(e)
            await websocket.send("Error")

    elif query_ask == "get_config":
        try:
            password = query.split("_%_")[1]
            print(password)
            if password == config_password:
                # read config.json
                try:
                    with open("config.json") as f:
                        config = json.load(f)
                    # send config
                    await websocket.send(json.dumps(config))
                except Exception as e:
                    print(e)
                    await websocket.send("Error")
            else:
                await websocket.send("Invalid query or format")

        except Exception as e:
            print(e)
            await websocket.send("Error")


    else:
        await websocket.send("Invalid query or format")


async def main():
    async with websockets.serve(diskord, host, port):
        print(f"Server started, listening on port {port}")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
