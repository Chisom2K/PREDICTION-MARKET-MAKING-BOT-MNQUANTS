# PREDICTION-MARKET-MAKING-BOT-MNQUANTS

This project aims to develop an algorithmic market-making bot for trading on prediction markets like [Kalshi](https://kalshi.com/api) and [Polymarket](https://polymarket.com/). The bot is designed to provide liquidity, manage risks, and optimize trading strategies by automating the process of placing buy and sell orders based on theoretical pricing models.
---

## Trading System

### System Architecture
The bot uses an asynchronous architecture with the following key components:

1. **Data Acquisition**:
   - `yfinance_client`: Fetches S&P 500 price data for market alignment.
   - `kalshi_websocket.py` & `kalshi_client.py`: Interfaces with Kalshi APIs for order book updates and trade fills.

2. **State Management**:
   - `state.py`: Maintains trading state, including order book snapshots, positions, and synchronization with market data.

3. **Order Execution**:
   - `market_maker.py`: Manages placing and canceling orders, ensuring alignment with trading logic and market conditions.

4. **Strategy**:
   - `strategy.py`: Placeholder for future decision-making logic based on market signals.

5. **Utilities**:
   - `market_tickers.py`: Handles trading schedules, market tickers, and price rounding.

6. **Logging**:
   - System-wide logging is implemented to track significant events (e.g., S&P price updates, order placements, and connection issues).
   - Logs are output to both a log file (`trading.log`) and the console for real-time monitoring.

### Key Features
- **Real-Time Market Updates**: Maintains synchronization with Kalshi's order book and price data from Yahoo Finance.
- **Dynamic Order Management**: Places and cancels orders based on market changes and trading strategy.
- **Asynchronous Operations**: Ensures low-latency responses to market events.
- **Fault Tolerance**: Handles API errors, disconnections, and unexpected failures through retries and reconnections.
- **Comprehensive Logging**: Logs key events and errors for debugging and analysis.


## Strategy
---
Still in development...

---

## Example Usage

### Running the Bot
```bash
python3 main.py
