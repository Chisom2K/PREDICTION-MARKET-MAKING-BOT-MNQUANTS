import asyncio
from market_maker import OrderManager
from state import TradingState
import time

class Strategy():

    def __init__(self, om: OrderManager, market: str, update: asyncio.Event, state: TradingState):
        self.order_manager = om
        self.update = update 
        self.market = market 
        self.state = state
#Further addtitions will be implemented once strategy is in place