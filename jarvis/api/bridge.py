"""
jarvis/api/bridge.py
Bridge to send events from synchronous JARVIS code to the WebSocket server.
"""

import requests
import json

def send_event(event_type: str, data: dict):
    """
    Since we can't easily call async code from sync code without a lot of boilerplate,
    we'll use a simple internal HTTP trigger or just a shared state.
    Actually, for this project, let's just use a simple HTTP POST to the FastAPI server
    which then broadcasts via WebSockets.
    """
    try:
        # We'll add a simple POST endpoint to server.py for this
        url = "http://localhost:8000/broadcast"
        payload = {"type": event_type, "data": data}
        requests.post(url, json=payload, timeout=0.1)
    except:
        pass
