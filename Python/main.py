import asyncio
import websockets

connected_clients = set()

async def handle_client(websocket):
    connected_clients.add(websocket)
    print("Client connected")
    try:
        async for message in websocket:
            print(f"Received: {message}")
    except websockets.ConnectionClosed:
        print("Client disconnected")
    finally:
        connected_clients.remove(websocket)

async def console_input():
    loop = asyncio.get_event_loop()
    while True:
        msg = await loop.run_in_executor(None, input, ">>> ")  # blocking call in async
        to_remove = set()
        for ws in connected_clients:
            try:
                await ws.send(msg)
            except:
                to_remove.add(ws)
        connected_clients.difference_update(to_remove)

async def main():
    server = await websockets.serve(handle_client, "localhost", 8080)
    print("Server running on ws://localhost:8080")
    await asyncio.gather(server.wait_closed(), console_input())

if __name__ == "__main__":
    asyncio.run(main())
