import logging
from requests_sse import EventSource
import requests
from dotenv import load_dotenv
import os

load_dotenv()
alpaca_key = os.getenv('alpaca_key')
alpaca_secret = os.getenv('alpaca_secret')

def main():
    logging.info("START")
    

if __name__ == "__main__":

    url = "https://data.alpaca.markets/v1beta1/news?start=2025-01-01T00%3A00%3A00Z&end=2025-02-01T00%3A00%3A00Z&sort=desc&symbols=BTCUSD&limit=50"

    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": alpaca_key,
        "APCA-API-SECRET-KEY": alpaca_secret
    }

    response = requests.get(url, headers=headers)

    print(response.text)