import websocket
import json
import signal
import threading
import time


# Alpaca API credentials
ALPACA_API_KEY = "PKTLERXUHCZNXYCDCTXJ"
ALPACA_API_SECRET = "npImKaBQsjQUf9ClkbdhztwCRGLqS489KphsVL0i"

# WebSocket endpoint
WEBSOCKET_URL = "wss://stream.data.alpaca.markets/v2/iex"  # SIP feed (premium)
# For free tier, use "iex" feed instead of "sip":
# WEBSOCKET_URL = "wss://stream.data.alpaca.markets/v2/iex"

# Global variable for WebSocket instance
ws = None

def on_open(ws):
    print("WebSocket connection opened.")
    # Authenticate with Alpaca
    auth_message = {
        "action": "auth",
        "key": ALPACA_API_KEY,
        "secret": ALPACA_API_SECRET
    }
    ws.send(json.dumps(auth_message))

    # Subscribe to AAPL stock trades
    subscribe_message = {
        "action": "subscribe",
        "trades": ["AAPL"],  # Subscribe to trades for AAPL
        "quotes": ["AMD","CLDR"],  # You can also subscribe to quotes
        "bars": ["*"]     # Or bars (OHLC)
    }
    ws.send(json.dumps(subscribe_message))

def on_message(ws, message):
    data = json.loads(message)
    print("Message received:", json.dumps(data, indent=2))

def on_error(ws, error):
    print("Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("WebSocket connection closed.")
    print(f"Close status code: {close_status_code}, message: {close_msg}")

def run_websocket():
    global ws
    websocket.enableTrace(False)  # Set to True for debugging
    ws = websocket.WebSocketApp(
        WEBSOCKET_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()

def close_websocket(signum, frame):
    """
    Signal handler to close the WebSocket connection gracefully.
    """
    global ws
    if ws:
        print("Closing WebSocket connection...")
        ws.close()
    print("Exiting script.")
    exit(0)

if __name__ == "__main__":
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, close_websocket)  # Handle Ctrl+C
    signal.signal(signal.SIGTERM, close_websocket)  # Handle termination signals

    try:
        websocket_thread = threading.Thread(target=run_websocket)
        websocket_thread.start()

        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        close_websocket(None, None)