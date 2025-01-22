import websocket
import json
import signal
import threading
import time
import os

from quixstreams import Application
import logging

from dotenv import load_dotenv
import os

load_dotenv()
# Alpaca API credentials
ALPACA_API_KEY = os.getenv('alpaca_key')
ALPACA_API_SECRET = os.getenv('alpaca_secret')


# WebSocket endpoint for Alpaca crypto data
WEBSOCKET_URL = "wss://stream.data.alpaca.markets/v1beta3/crypto/us"

# Global WebSocket instance
ws = None

def kafkiano(info=None):
    app = Application(
        broker_address="localhost:19092",
        loglevel="DEBUG"
    )

    with app.get_producer() as producer:
        producer.produce(
            topic="bitcoin_price",
            key="crypto",
            value=json.dumps(info)
        )
        logging.info("Price Sent")

def on_open(ws):
    print("WebSocket connection opened.")

    # Authenticate with Alpaca
    auth_message = {
        "action": "auth",
        "key": ALPACA_API_KEY,
        "secret": ALPACA_API_SECRET
    }
    ws.send(json.dumps(auth_message))

    # Subscribe to Bitcoin (BTC/USD) trades
    subscribe_message = {
        "action": "subscribe",
        "trades": [],  # Subscribe to trades
        "quotes": [],           # Optional: Subscribe to quotes
        "bars": ["BTC/USD"]              # Optional: Subscribe to OHLC bars
    }
    ws.send(json.dumps(subscribe_message))

def on_message(ws, message):
    data = json.loads(message)

    if isinstance(data, list):  # Messages are usually sent as a list
        for msg in data:
            message_type = msg.get("T")
            symbol = msg.get("S")

            if message_type == "t":
                print(f"Trade: {symbol} - Price: {msg['p']}, Size: {msg['s']}, Exchange: {msg['x']}")
            elif message_type == "q":
                print(f"Quote: {symbol} - Bid: {msg['bp']}@{msg['bs']}, Ask: {msg['ap']}@{msg['as']}")
            elif message_type == "b":
                print(f"Bar: {symbol} - Open: {msg['o']}, High: {msg['h']}, Low: {msg['l']}, Close: {msg['c']}, Volume: {msg['v']}")
                kafkiano(info={
                    "open":msg['o'],
                    "high":msg['h'],
                    "low":msg['l'],
                    "close":msg['c'],
                    "volume":msg['v']
                })
            else:
                print("Unknown message type:", msg)
    else:
        print("Non-list message received:", data)
    # print("Message received:", json.dumps(data, indent=2))

def on_error(ws, error):
    print("Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("WebSocket connection closed.")
    print(f"Close status code: {close_status_code}, message: {close_msg}")

def run_websocket():
    global ws
    websocket.enableTrace(False)  # Enable for debugging if needed
    ws = websocket.WebSocketApp(
        WEBSOCKET_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever(ping_interval=30, ping_timeout=10)

def close_websocket(signum, frame):
    global ws
    if ws:
        print("Closing WebSocket connection...")
        ws.close()
    print("Exiting script.")
    os._exit(0)  # Forcefully exit all threads and connections

if __name__ == "__main__":
    # Register signal handlers for graceful termination
    signal.signal(signal.SIGINT, close_websocket)
    signal.signal(signal.SIGTERM, close_websocket)

    try:
        websocket_thread = threading.Thread(target=run_websocket)
        websocket_thread.start()

        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        close_websocket(None, None)