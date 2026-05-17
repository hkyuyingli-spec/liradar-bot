import requests
import pandas as pd
import yfinance as yf

COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
DEFILLAMA_BASE_URL = "https://api.llama.fi"
DEFILLAMA_YIELDS_URL = "https://yields.llama.fi"

def get_historical_data(symbol, period="1y", interval="1d"):
    """Fetch historical data using yfinance with improved error handling."""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        if df is None or df.empty:
            return None
        return df
    except Exception as e:
        # Returning None so the UI can handle the missing data gracefully
        return None

def get_token_price(token_id):
    """Fetch current price of a token from CoinGecko."""
    try:
        url = f"{COINGECKO_BASE_URL}/simple/price"
        params = {
            "ids": token_id.lower(),
            "vs_currencies": "usd",
            "include_24hr_change": "true"
        }
        response = requests.get(url, params=params)
        data = response.json()
        if token_id in data:
            return data[token_id]
        return None
    except Exception as e:
        return None

def get_defi_protocols():
    """Fetch top DeFi protocols from DeFiLlama."""
    try:
        url = f"{DEFILLAMA_BASE_URL}/protocols"
        response = requests.get(url)
        return response.json()
    except Exception as e:
        return []

def get_protocol_data(protocol_slug):
    """Fetch specific protocol data from DeFiLlama."""
    try:
        url = f"{DEFILLAMA_BASE_URL}/protocol/{protocol_slug}"
        response = requests.get(url)
        return response.json()
    except Exception as e:
        return None

def get_yield_pools():
    """Fetch top yield pools from DeFiLlama."""
    try:
        url = f"{DEFILLAMA_YIELDS_URL}/pools"
        response = requests.get(url)
        return response.json()["data"]
    except Exception as e:
        return []

def get_top_crypto_prices():
    """Fetch top 10 crypto prices from CoinGecko."""
    try:
        url = f"{COINGECKO_BASE_URL}/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 10,
            "page": 1,
            "sparkline": "false"
        }
        response = requests.get(url, params=params)
        return response.json()
    except Exception as e:
        return []

def get_global_market_data():
    """Fetch total market cap and BTC/ETH dominance."""
    try:
        url = f"{COINGECKO_BASE_URL}/global"
        response = requests.get(url)
        data = response.json()
        return data.get("data", {})
    except Exception as e:
        return {}

def get_fear_and_greed_index():
    """Fetch Fear & Greed Index."""
    try:
        url = "https://api.alternative.me/fng/"
        response = requests.get(url)
        data = response.json()
        if data["data"]:
            return data["data"][0]
        return None
    except Exception as e:
        return None

def search_token_id(query):
    """Simple search to map token symbol/name to CoinGecko ID."""
    try:
        url = f"{COINGECKO_BASE_URL}/search"
        params = {"query": query}
        response = requests.get(url, params=params)
        data = response.json()
        if data["coins"]:
            return data["coins"][0]["id"]
        return None
    except Exception as e:
        return None
