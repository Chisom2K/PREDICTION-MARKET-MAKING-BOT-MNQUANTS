# PREDICTION-MARKET-MAKING-BOT-MNQUANTS

This project aims to develop an algorithmic market-making bot for trading on prediction markets like [Kalshi](https://kalshi.com/api) and [Polymarket](https://polymarket.com/). The bot is designed to provide liquidity, manage risks, and optimize trading strategies by automating the process of placing buy and sell orders based on theoretical pricing models.


## Trading System
---
### Components

### 1. **yfinance_client**
- **Purpose**: Fetches the real-time price of the S&P 500 index asynchronously.
- **Key Features**:
  - Periodically fetches the price using `yfinance`.
  - Updates the shared `TradingState` with the latest price.
  - Triggers an event to notify other components when the price is updated.
- **Integration**:
  - Works with the `TradingState` object for state updates.
  - Uses asyncio for non-blocking periodic updates.

### 2. **KalshiHTTPClient**
- **Purpose**: Handles authenticated API interactions with the Kalshi HTTP API.
- **Key Features**:
  - Supports `GET`, `POST`, `PUT`, and `DELETE` requests.
  - Manages login and token-based authentication.
  - Provides methods to fetch events, markets, balances, and positions.
- **Integration**:
  - Used for RESTful interactions with Kalshi's API.

### 3. **KalshiWebSocket**
- **Purpose**: Manages real-time connections to Kalshi's WebSocket API for live updates.
- **Key Features**:
  - Listens to `orderbook_delta` and `fill` updates.
  - Updates the `TradingState` based on real-time data.
  - Maintains a persistent connection and reconnects on failure.
- **Integration**:
  - Relies on the `yfinance_client` for market price.
  - Notifies the `TradingState` of real-time updates.

### 4. **TradingState**
- **Purpose**: Maintains the shared state of the trading bot.
- **Key Features**:
  - Tracks order book snapshots, deltas, and fills.
  - Updates the state with the latest S&P 500 price fetched by the `yfinance_client`.
  - Ensures consistent data flow between components.
- **Integration**:
  - Shared by the `yfinance_client`, `KalshiHTTPClient`, and `KalshiWebSocket`.

### 5. **OrderManager**
- **Purpose**: Manages order creation, execution, and cancellation.
- **Key Features**:
  - Interfaces with the `KalshiHTTPClient` to execute orders.
  - Handles order management logic based on the current state.
- **Integration**:
  - Utilized by both the `KalshiWebSocket` and `yfinance_client`.

### 6. **Logs**
- **Purpose**: Tracks the bot's operations and events for debugging and monitoring.
- **Setup**:
  - Logs are stored in `trading.log`.
  - Configured with `logging.basicConfig` in the main file.
- **Usage**:
  - Each component logs critical events such as:
    - Successful HTTP logins.
    - S&P price updates.
    - WebSocket connection statuses.
    - Errors and exceptions.
  - Example:
    ```text
    2024-11-24 22:05:12,386 - INFO - Success logging in to Kalshi! Bearer token obtained.
    2024-11-24 22:05:12,659 - INFO - Subscribing to market INXD-24NOV25-B5975
    2024-11-24 22:05:12,717 - INFO - Received Kalshi orderbook snapshot: {'bids': {}, 'asks': {}}
    ```

## Strategy
---
Still in development...

---

## Example Usage

### Running the Bot
```bash
python3 main.py
