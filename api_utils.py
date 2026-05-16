import requests
import pandas as pd

COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
DEFILLAMA_BASE_URL = "https://api.llama.fi"
DEFILLAMA_YIELDS_URL = "https://yields.llama.fi"

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
