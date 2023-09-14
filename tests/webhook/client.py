import asyncio
import websockets

async def hello():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        query = input("Enter query separated by _%_: ")
        await websocket.send(query)
        print(f"> {query}")

        websocket_feedback = await websocket.recv()
        print(f"< {websocket_feedback}")


if __name__ == "__main__":
    asyncio.run(hello())
