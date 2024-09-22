# main.py

import config
from Clients.kalshi_client import ExchangeClient

email = config.email
password = config.password

exchange_client = ExchangeClient(
    exchange_api_base=config.KALSHI_API_BASE,
    email=email,
    password=password
)