import os

# API Keys Configuration
NEWS_API_KEY = "8d2b07691ab54b1592d99b5fa6dcc948"
GNEWS_API_KEY = "dd0490acae3413a8b95335a8ace58347"
ALPHA_VANTAGE_API_KEY = "MJZ6K7M0IZSQVHJ5"
METALS_API_KEY = "cflqymfx6mzfe1pw3p4zgy13w9gj12z4aavokqd5xw4p8xeplzlwyh64fvrv"
POSTGRESQL_URL = "postgresql://postgres:vVMyqWjrqgVhEnwyFifTQxkDtPjQutGb@interchange.proxy.rlwy.net:30451/railway"
TRADINGECONOMICS_API = os.getenv("TRADINGECONOMICS_API")

# Financial Instruments to Track
INSTRUMENTS = {
    "gold": "XAUUSD",
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "dow jones": "DJI",
    "nasdaq": "IXIC",
    "eur/usd": "EURUSD",
    "gbp/usd": "GBPUSD"
}

DB_NAME = "railway"
DB_USER = "postgres"
DB_PASSWORD = "vVMyqWjrqgVhEnwyFifTQxkDtPjQutGb"  # ✅ Use the correct password from Railway
DB_HOST = "interchange.proxy.rlwy.net"
DB_PORT = "30451"



# Yahoo Finance Symbols for Real-Time Prices
MARKET_SYMBOLS = {
    "gold": "XAUUSD=X",
    "bitcoin": "BTC-USD",
    "ethereum": "ETH-USD",
    "dow jones": "^DJI",
    "nasdaq": "^IXIC",
    "eur/usd": "EURUSD=X",
    "gbp/usd": "GBPUSD=X"
}

