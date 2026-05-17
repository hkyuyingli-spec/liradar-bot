import requests
import pandas as pd
import yfinance as yf
import streamlit as st

COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
DEFILLAMA_BASE_URL = "https://api.llama.fi"
DEFILLAMA_YIELDS_URL = "https://yields.llama.fi"

def _get_coingecko_headers():
    """Helper to get headers for CoinGecko API if key is present."""
    headers = {}
    try:
        # Check for API key in Streamlit secrets
        api_key = st.secrets.get("COINGECKO_API_KEY")
        if api_key:
            # CoinGecko Demo/Pro API keys use this header
            headers["x-cg-demo-api-key"] = api_key
    except:
        pass
    return headers

def get_historical_data(symbol, period="1y", interval="1d"):
    """Fetch historical data using yfinance with improved error handling."""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        if df is None or df.empty:
            return None
        return df
    except Exception as e:
        return None

def get_token_price(token_id):
    """Fetch current price of a token from CoinGecko with fallback."""
    try:
        url = f"{COINGECKO_BASE_URL}/simple/price"
        params = {
            "ids": token_id.lower(),
            "vs_currencies": "usd",
            "include_24hr_change": "true"
        }
        response = requests.get(url, params=params, headers=_get_coingecko_headers(), timeout=10)
        data = response.json()
        if token_id in data:
            return data[token_id]
        return None
    except Exception as e:
        # Fallback to yfinance if CoinGecko fails for certain tokens
        try:
            symbol_map = {"bitcoin": "BTC-USD", "ethereum": "ETH-USD", "solana": "SOL-USD"}
            yf_symbol = symbol_map.get(token_id.lower())
            if yf_symbol:
                ticker = yf.Ticker(yf_symbol)
                price = ticker.fast_info['last_price']
                change = ticker.fast_info['year_to_date_return'] # Not exactly 24h, but a backup
                return {"usd": price, "usd_24h_change": change}
        except:
            pass
        return None

def get_defi_protocols():
    """Fetch top DeFi protocols from DeFiLlama."""
    try:
        url = f"{DEFILLAMA_BASE_URL}/protocols"
        response = requests.get(url, timeout=10)
        return response.json()
    except Exception as e:
        return []

def get_top_crypto_prices():
    """Fetch top 10 crypto prices from CoinGecko with yfinance fallback."""
    try:
        url = f"{COINGECKO_BASE_URL}/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 10,
            "page": 1,
            "sparkline": "false"
        }
        response = requests.get(url, params=params, headers=_get_coingecko_headers(), timeout=10)
        if response.status_code == 200:
            return response.json()
        raise Exception("CoinGecko Rate Limited")
    except Exception as e:
        # Backup: Fetch from yfinance
        try:
            backup_symbols = ["BTC-USD", "ETH-USD", "USDT-USD", "BNB-USD", "SOL-USD", "XRP-USD", "USDC-USD", "ADA-USD", "STETH-USD", "DOGE-USD"]
            backup_data = []
            for sym in backup_symbols:
                ticker = yf.Ticker(sym)
                info = ticker.fast_info
                backup_data.append({
                    "name": sym.split('-')[0],
                    "symbol": sym.split('-')[0].lower(),
                    "current_price": info['last_price'],
                    "price_change_percentage_24h": 0.0, # yfinance fast_info doesn't easily give 24h %
                    "market_cap": info.get('market_cap', 0)
                })
            return backup_data
        except:
            return []

def get_global_market_data():
    """Fetch total market cap and BTC/ETH dominance from CoinGecko."""
    try:
        url = f"{COINGECKO_BASE_URL}/global"
        response = requests.get(url, headers=_get_coingecko_headers(), timeout=10)
        data = response.json()
        return data.get("data", {})
    except Exception as e:
        return {}

def get_fear_and_greed_index():
    """Fetch Fear & Greed Index."""
    try:
        url = "https://api.alternative.me/fng/"
        response = requests.get(url, timeout=10)
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
        response = requests.get(url, params=params, headers=_get_coingecko_headers(), timeout=10)
        data = response.json()
        if data["coins"]:
            return data["coins"][0]["id"]
        return None
    except Exception as e:
        return None
