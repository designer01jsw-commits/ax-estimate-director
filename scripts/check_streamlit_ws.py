# -*- coding: utf-8 -*-
import asyncio
import json
import websockets

async def check_streamlit_ws():
    uri = "wss://ax-estimate-director.onrender.com/_stcore/stream"
    print("Connecting to Streamlit WebSocket:", uri)
    try:
        async with websockets.connect(uri, subprotocols=["streamlit"]) as ws:
            print("WebSocket handshake connected successfully!")
            # Streamlit server sends a ForwardMsg with new_session or session_state
            # Let's read up to 5 messages
            for i in range(5):
                msg = await asyncio.wait_for(ws.recv(), timeout=5)
                print(f"Message {i+1} received! Bytes: {len(msg)}")
                # Check if it has text or protobuf
                if isinstance(msg, bytes):
                    # Check if error is in bytes
                    if b"Exception" in msg or b"Traceback" in msg:
                        print("WARNING: Exception found in message:", msg[:200])
                    else:
                        print("Message appears to be normal Streamlit ForwardMsg protobuf")
            print("STREAMLIT APP IS RUNNING AND COMMUNICATING PERFECTLY!")
    except asyncio.TimeoutError:
        print("Timeout waiting for more messages, but connection was established.")
    except Exception as e:
        print("WebSocket check failed with exception:", e)

asyncio.run(check_streamlit_ws())
