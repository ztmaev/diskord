import asyncio
import json
import websockets

thread_info_json_path = "temp/ids_config.json"
config_password = "password"
port = 8765
host = "0.0.0.0"

def get_current_time():
    import datetime
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def logger(message):
    # add timestamp
    message = f"[{get_current_time()}] {message}"
    try:
        with open("server.log", "r") as f:
            pass
    except FileNotFoundError:
        with open("server.log", "w") as f:
            pass
    # append message
    with open("server.log", "a") as f:
        f.write(message + "\n")

async def diskord(websocket):
    query = await websocket.recv()
    logger(f"Received: {query}")
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
            logger(f"Error: {e}")
            await websocket.send("Error")

    elif query_ask == "get_config":
        try:
            password = query.split("_%_")[1]
            if password == config_password:
                # read config.json
                try:
                    with open("config.json") as f:
                        config = json.load(f)
                    # send config
                    await websocket.send(json.dumps(config))
                except Exception as e:
                    logger(f"Error: {e}")
                    await websocket.send("Error")
            else:
                await websocket.send("Invalid query or format")

        except Exception as e:
            logger(f"Error: {e}")
            await websocket.send("Error")

    elif query_ask == "get_upload_info":
        # read json and get each subfile's info, format {filename: "gshjs", file_url: "https://..."}
        file_id = query.split("_%_")[1]
        try:
            with open(f"db_dir/{file_id}.json") as f:
                file_info = json.load(f)
            # send file info
            await websocket.send(json.dumps(file_info))
        except Exception as e:
            logger(f"Error: {e}")
            await websocket.send("Error")



    else:
        await websocket.send("Invalid query or format")


async def main():
    async with websockets.serve(diskord, host, port):
        logger(f"Server started, listening on port {port}")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
