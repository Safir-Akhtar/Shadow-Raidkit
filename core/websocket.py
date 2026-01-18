# core/websocket.py - Shadow Tools WebSocket server + broadcast
import asyncio
import json
import websockets
from .config import CONNECTED_WS_CLIENTS, PORT_WS
from .commands import handle_frontend_command

async def ws_handler(websocket):
    CONNECTED_WS_CLIENTS.add(websocket)
    print(f"[Shadow WS] New frontend connected - total clients: {len(CONNECTED_WS_CLIENTS)}")
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                await handle_frontend_command(data)
            except json.JSONDecodeError:
                print("[Shadow WS] Invalid JSON from frontend")
            except Exception as e:
                print(f"[Shadow WS] Command processing error: {e}")
    except websockets.exceptions.ConnectionClosed:
        print("[Shadow WS] Frontend disconnected normally")
    except Exception as e:
        print(f"[Shadow WS] Connection error: {e}")
    finally:
        CONNECTED_WS_CLIENTS.remove(websocket)
        print(f"[Shadow WS] Client disconnected - remaining: {len(CONNECTED_WS_CLIENTS)}")

def broadcast(data: dict):
    """Sab connected frontends ko real-time update bhej do"""
    try:
        payload = json.dumps(data)
        for ws in list(CONNECTED_WS_CLIENTS):
            try:
                asyncio.create_task(ws.send(payload))
            except:
                CONNECTED_WS_CLIENTS.remove(ws)
    except Exception as e:
        print(f"[Shadow Broadcast] Error: {e}")

async def start_ws_server():
    async with websockets.serve(ws_handler, "localhost", PORT_WS):
        print(f"[Shadow Tools] WebSocket beast server started on ws://localhost:{PORT_WS}")
        await asyncio.Future()  # Run forever