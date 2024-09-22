import time
import uuid
import threading
from tabulate import tabulate
import pprint
from Clients.kalshi_client import HttpError
from Clients.kalshi_client import ExchangeClient

class KalshiMarketMaker:
    def __init__(self, exchange_client, market_ticker):
        self.exchange_client = exchange_client
        self.market_ticker = market_ticker

    def get_orderbook(self):
        try:
            orderbook = self.exchange_client.get_orderbook(ticker=self.market_ticker)
            return orderbook['orderbook']
        except Exception as e:
            print(f"Error fetching orderbook for {self.market_ticker}: {e}")
            return None

    def get_bbo(self):
        orderbook = self.get_orderbook()
        if orderbook:
            best_bid = orderbook['yes'][-1][0] if orderbook['yes'] else 0
            best_bid_quantity = orderbook['yes'][-1][1] if orderbook['yes'] else 0
            best_ask = 100 - orderbook['no'][-1][0] if orderbook['no'] else 100
            best_ask_quantity = orderbook['no'][-1][1] if orderbook['no'] else 0
            mid = (best_bid + best_ask) / 2

            return {
                'bid': best_bid,
                'bid_quantity': best_bid_quantity,
                'ask': best_ask,
                'ask_quantity': best_ask_quantity,
                'mid': mid
            }
        return None

    def print_bbo(self):
        bbo = self.get_bbo()
        if bbo:
            table = [[
                bbo['bid_quantity'],
                bbo['bid'],
                bbo['mid'],
                bbo['ask'],
                bbo['ask_quantity']
            ]]
            headers = ['BidSz', 'Bid', 'Mid', 'Ask', 'AskSz']
            print(tabulate(table, headers=headers, tablefmt='fancy_grid'))
        else:
            print("Unable to fetch BBO data")

    def get_positions(self):
        try:
            positions = self.exchange_client.get_positions(ticker=self.market_ticker)
            return positions['market_positions']
        except Exception as e:
            print(f"Error fetching positions for {self.market_ticker}: {e}")
            return None

    def get_my_orders(self):
        try:
            orders = self.exchange_client.get_orders(ticker=self.market_ticker)
            return orders['orders']
        except Exception as e:
            print(f"Error fetching orders for {self.market_ticker}: {e}")
            return None

    def print_my_orders(self):
        orders = self.get_my_orders()
        if not orders:
            print("No orders found.")
            return

        # Group orders by ticker
        orders_by_ticker = {}
        for order in orders:
            ticker = order['ticker']
            if ticker not in orders_by_ticker:
                orders_by_ticker[ticker] = {'Yes': None, 'No': None}

            side = order['side'].capitalize()

            # Update or set the order for this side
            if orders_by_ticker[ticker][side] is None or order['remaining_count'] > 0:
                orders_by_ticker[ticker][side] = order

        for ticker, ticker_orders in orders_by_ticker.items():
            print(f"\nTicker: {ticker}")

            table_data = []
            for side, order in ticker_orders.items():
                if order:
                    action = order['action'].capitalize()
                    if side == 'Yes':
                        price = order['yes_price']
                    else:  # No side
                        price = 100 - order['no_price']  # Convert No price to Yes equivalent
                    quantity = order['remaining_count']
                    fill_count = order['place_count'] - order['remaining_count']

                    table_data.append([side, action, price, quantity, fill_count])

            # Sort the table data so that 'Yes' always comes before 'No'
            table_data.sort(key=lambda x: x[0], reverse=True)

            headers = ['Side', 'Action', 'Price', 'Quantity', 'Fill Count']
            print(tabulate(table_data, headers=headers, tablefmt='pretty'))

    def create_quote(self, theo, edge_requirement):
        bbo = self.get_bbo()
        if bbo:
            bid = min(max(1, theo - edge_requirement), bbo['bid'])
            ask = max(min(99, theo + edge_requirement), bbo['ask'])
            return {'bid': bid, 'ask': ask}
        return None

    def create_quote_strict(self, theo, edge_requirement):
        bid = max(1, theo - edge_requirement)
        ask = min(99, theo + edge_requirement)
        return {'bid': bid, 'ask': ask}

    def send_quote(self, quote, quantity):
        if not quote:
            print("No valid quote to send")
            return

        try:
            # Place bid (limit buy yes)
            bid_params = {
                'ticker': self.market_ticker,
                'client_order_id': str(uuid.uuid4()),
                'type': 'limit',
                'action': 'buy',
                'side': 'yes',
                'count': quantity,
                'yes_price': quote['bid'],
                'no_price': None,
            }
            bid_order = self.exchange_client.create_order(**bid_params)

            # Place ask (limit buy no)
            ask_params = {
                'ticker': self.market_ticker,
                'client_order_id': str(uuid.uuid4()),
                'type': 'limit',
                'action': 'buy',
                'side': 'no',
                'count': quantity,
                'yes_price': None,
                'no_price': 100 - quote['ask'],
            }
            ask_order = self.exchange_client.create_order(**ask_params)

            return {'bid_order': bid_order, 'ask_order': ask_order}
        except Exception as e:
            print(f"Error sending quote for {self.market_ticker}: {e}")
            return None

    def print_positions(self):
        positions = self.get_positions()
        if not positions:
            print("No positions found.")
            return

        table_data = []
        for position_group in positions:
            if isinstance(position_group, list):
                for position in position_group:
                    self._add_position_to_table_data(position, table_data)
            elif isinstance(position_group, dict):
                self._add_position_to_table_data(position_group, table_data)

        if table_data:
            headers = ['Ticker', 'Position', 'Exposure', 'Resting Orders', 'Realized PNL', 'Total Traded']
            print(tabulate(table_data, headers=headers, tablefmt='pretty'))
        else:
            print("No valid position data found.")

    def _add_position_to_table_data(self, position, table_data):
        ticker = position['ticker']
        pos = position['position']
        exposure = f"${position['market_exposure'] / 100:.2f}"
        resting_orders = position['resting_orders_count']
        realized_pnl = f"${position['realized_pnl'] / 100:.2f}"
        total_traded = f"${position['total_traded'] / 100:.2f}"

        table_data.append([
            ticker,
            pos,
            exposure,
            resting_orders,
            realized_pnl,
            total_traded
        ])

    def send_bid(self, price, quantity):
        try:
            bid_params = {
                'ticker': self.market_ticker,
                'client_order_id': str(uuid.uuid4()),
                'type': 'limit',
                'action': 'buy',
                'side': 'yes',
                'count': quantity,
                'yes_price': price,
                'no_price': None,
            }
            bid_order = self.exchange_client.create_order(**bid_params)
            return bid_order
        except Exception as e:
            print(f"Error sending bid for {self.market_ticker}: {e}")
            return None

    def send_ask(self, price, quantity):
        try:
            ask_params = {
                'ticker': self.market_ticker,
                'client_order_id': str(uuid.uuid4()),
                'type': 'limit',
                'action': 'buy',
                'side': 'no',
                'count': quantity,
                'yes_price': None,
                'no_price': 100 - price,
            }
            ask_order = self.exchange_client.create_order(**ask_params)
            return ask_order
        except Exception as e:
            print(f"Error sending ask for {self.market_ticker}: {e}")
            return None


    def pull_all_quotes(self):
        try:
            orders = self.get_my_orders()
            print(f"Retrieved {len(orders)} orders.")
            
            if not orders:
                print("No orders to pull.")
                return []

            cancelled_orders = []
            already_cancelled = []
            other_errors = []

            for order in orders:
                order_id = order['order_id']
                print(f"Attempting to cancel order: {order_id}")
                
                order_status = self.exchange_client.get_order(order_id)
                print(f"Order {order_id} status: {order_status}")
                
                if order_status['order']['status'] == 'canceled':
                    print(f"Order {order_id} is already cancelled.")
                    already_cancelled.append(order_id)
                    continue

                time.sleep(1)  # Wait for 1 second before attempting to cancel

                try:
                    result = self.exchange_client.cancel_order(order_id)
                    if result['order']['remaining_count'] == 0:
                        cancelled_orders.append(result)
                        print(f"Successfully cancelled order: {order_id}")
                        print(f"Cancelled order details: {result}")
                    else:
                        print(f"Order {order_id} not fully cancelled. Remaining count: {result['order']['remaining_count']}")
                except HttpError as e:
                    print(f"Error cancelling order {order_id}: {e}")
                    print(f"Full error response: {e.reason}")
                    if e.status == 404:
                        already_cancelled.append(order_id)
                        print(f"Order not found: {order_id}")
                    else:
                        other_errors.append((order_id, str(e)))
                except Exception as e:
                    print(f"Unexpected error cancelling order {order_id}: {e}")
                    other_errors.append((order_id, str(e)))

            print(f"Successfully cancelled {len(cancelled_orders)} orders.")
            if already_cancelled:
                print(f"Orders already cancelled or not found: {len(already_cancelled)}")
                for order_id in already_cancelled:
                    print(f"  - {order_id}")
            if other_errors:
                print(f"Other errors occurred for {len(other_errors)} orders:")
                for order_id, error in other_errors:
                    print(f"  - Order {order_id}: {error}")

            return cancelled_orders

        except Exception as e:
            print(f"Error pulling quotes for {self.market_ticker}: {e}")
            return None

    def pull_side_quotes(self, side):
        if side not in ['yes', 'no']:
            print("Invalid side. Use 'yes' or 'no'.")
            return

        try:
            orders = self.get_my_orders()
            if not orders:
                print("No orders to pull.")
                return

            cancelled_orders = []
            for order in orders:
                if order['side'] == side:
                    order_id = order['order_id']
                    try:
                        result = self.exchange_client.cancel_order(order_id)
                        cancelled_orders.append(result)
                    except Exception as e:
                        print(f"Error cancelling order {order_id}: {e}")

            print(f"Pulled {len(cancelled_orders)} {side} orders.")
            return cancelled_orders
        except Exception as e:
            print(f"Error pulling {side} quotes for {self.market_ticker}: {e}")
            return None