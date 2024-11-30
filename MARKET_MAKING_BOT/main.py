import kalshi_python
import config
import asyncio
import nest_asyncio
import logging
import pandas as pd
from Clients.kalshi_client import KalshiHTTPClient
from Clients.kalshi_websocket import KalshiClient
from state import TradingState
from market_maker import OrderManager
from Utils.market_tickers import *
from Clients.SPX import yfinance_client
import sys
import time
import datetime

api_base = "https://trading-api.kalshi.com/trade-api/v2"
demo_api_base = "https://demo-api.kalshi.co/trade-api/v2"
ws_base = "wss://trading-api.kalshi.com/trade-api/ws/v2"
demo_ws_base = "wss://demo-api.kalshi.co/trade-api/ws/v2"
email = config.email
password = config.password

async def main():
    
    logging.basicConfig(filename='trading.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s - %(funcName)s', level=logging.DEBUG)


    # Comment out to disable logging to console
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


    # Wait until the market is open (Comment out if you want to test the bot at any time)
    # if is_market_open():
    #     logging.info("Market is already open. Starting execution...")
    # else:
    #     next_day: int = int(time.mktime(time.strptime(str(get_next_trading_day()) + " 09:30:00", "%Y-%m-%d %H:%M:%S")))
    #     seconds: int = next_day - int(time.mktime(datetime.datetime.now().timetuple()))
    #     logging.info(f"{seconds} seconds until market open.")
    #     if seconds > 0:
    #         time.sleep(seconds)  # Wait only if seconds is positive
    #     logging.info("Market open, starting execution...")

    logging.info("Kalshi Trading System v2")

    MARKET = get_market_ticker()

    update = asyncio.Event()

    # Initialize the client
    kalshi_http_client = KalshiHTTPClient(email, password)
    om = OrderManager(kalshi_http_client, MARKET)
    # Include Strategy initialization here: 
    # strategy = Strategy(om, MARKET, update, state)
    state = TradingState(om, kalshi_http_client)
    yf_client = yfinance_client(update, state, om)
    kalshi_client = KalshiClient(demo_api_base, demo_ws_base, email, password, yf_client, state, update, MARKET)

    yf = asyncio.create_task(yf_client.run())
    kalshi = asyncio.create_task(kalshi_client.run())

    await yf
    await kalshi

if __name__ == "__main__":
    asyncio.run(main())