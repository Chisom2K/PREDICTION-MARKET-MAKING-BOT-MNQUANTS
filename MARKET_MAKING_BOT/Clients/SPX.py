import asyncio
import yfinance as yf
import logging 
from state import TradingState
from market_maker import OrderManager

class yfinance_client:
    """

    Asynchronous S&P 500 price fetcher using Yahoo Finance.

    """

    def __init__(self, update: asyncio.Event,om: OrderManager, state: TradingState) -> None:
        self.price: float = -1  
        self.update = update    
        self.state = state
        self.om = om

        self.REQUEST_DELAY = 10

    def get_spx(self):
      try:
          spx = yf.Ticker("^GSPC")
          price = spx.history(period="1d")['Close'].iloc[-1]
          logging.info(f"Fetched S&P 500 price: {price}")
          return price
      except Exception as e:
          logging.error(f"Error fetching S&P 500 price: {e}")
          return self.price  # Return the last known price in case of error
      
    def update_state(self, price): 
      self.state.update_sp(price)
      self.update.set()

    async def run(self) -> None:
        """
        Continuously fetch and update the S&P 500 price.
        """
        try:
            while True:
                price = await self.get_spx()
                if price != self.price:  # Only update if the price has changed
                    self.price = price
                    self.update_state(price)
                await asyncio.sleep(self.REQUEST_DELAY)  # Wait before fetching the price again
        except asyncio.CancelledError:
            logging.info("SPXFetcher run method cancelled. Exiting...")
        except Exception as e:
            logging.error(f"Unexpected error in SPXFetcher: {e}")

    def get_price(self) -> float:
        """
        Return the most recently fetched price.
        """
        return self.price

    # def get_vix():
    #   vix = yf.Ticker("^VIX")
    #   return vix.history(period="1d")['Close'].iloc[-1]