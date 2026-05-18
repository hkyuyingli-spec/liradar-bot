import streamlit as st
import bot_logic
import api_utils
import analysis
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="LiRadar - DeFi Analysis Bot",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Session State Initialization ---
if "last_updated" not in st.session_state:
    st.session_state.last_updated = datetime.now().strftime("%H:%M:%S")

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

# --- Theme Styling (Safe CSS) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #1a1a2e;
        color: #ffffff;
    }
    .main {
        background-color: #1a1a2e;
    }
    [data-testid="stMetric"] {
        background-color: #0f3460;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #16213e;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    [data-testid="stMetricLabel"] {
        color: #e0e0e0 !important;
    }
    [data-testid="stMetricValue"] {
        color: #f1c40f !important;
        font-weight: 800 !important;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        background-color: #e94560;
        color: white;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #ff4d6d;
    }
    .signal-card {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border: 1px solid #30363d;
    }
    .signal-success { background-color: rgba(40, 167, 69, 0.15); border-left: 5px solid #28a745; }
    .signal-danger { background-color: rgba(220, 53, 69, 0.15); border-left: 5px solid #dc3545; }
    .signal-warning { background-color: rgba(255, 193, 7, 0.1); border-left: 5px solid #ffc107; }
    </style>
    """, unsafe_allow_html=True)

# --- Data Fetching with Caching ---
@st.cache_data(ttl=300)
def fetch_fear_and_greed():
    return api_utils.get_fear_and_greed_index()

@st.cache_data(ttl=300)
def fetch_global_data():
    return api_utils.get_global_market_data()

@st.cache_data(ttl=300)
def fetch_top_crypto():
    return api_utils.get_top_crypto_prices()

@st.cache_data(ttl=300)
def fetch_defi_protocols():
    return api_utils.get_defi_protocols()

# --- Sidebar ---
with st.sidebar:
    st.title("📡 LiRadar")
    st.markdown("---")
    st.markdown("""
    ### Meet LiRadar
    I'm **LiRadar**, your professional DeFi analyst. 
    I scan the blockchain to find the best yields.
    """)
    
    st.markdown("### 📊 Yield Calculator")
    principal = st.number_input("Principal ($)", min_value=0.0, value=1000.0)
    apr = st.number_input("APR (%)", min_value=0.0, value=10.0)
    days = st.number_input("Days", min_value=1, value=365)
    
    if st.button("Calculate Returns"):
        res = bot_logic.process_yield_command(principal, apr, days)
        st.success(res)

    st.markdown("---")
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# --- Main Dashboard ---
st.title("📡 LiRadar Trading Dashboard")

# Tabs at the TOP
tab1, tab2, tab3 = st.tabs(["💬 LiRadar Chat", "📈 Algo Trading", "📊 Market LiRadar"])

with tab1:
    chat_container = st.container()

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Welcome back! LiRadar reporting for duty. How can I assist your portfolio today?"}
        ]

    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if prompt := st.chat_input("Ex: 'Price of Bitcoin' or 'Top DeFi protocols'"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        response = bot_logic.get_liradar_response(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

with tab2:
    st.header("Professional Algo Trading Dashboard")
    
    # Asset Selection
    col_a1, col_a2, col_a3 = st.columns([1, 1, 1])
    
    with col_a1:
        asset_type = st.selectbox("Asset Type", ["Cryptocurrencies", "DeFi Tokens", "Stocks", "Forex", "Custom"])
    
    with col_a2:
        if asset_type == "Cryptocurrencies":
            asset_options = {"Bitcoin": "BTC-USD", "Ethereum": "ETH-USD", "Solana": "SOL-USD", "BNB": "BNB-USD", "Cardano": "ADA-USD"}
            selected_asset = st.selectbox("Select Asset", list(asset_options.keys()))
            symbol = asset_options[selected_asset]
        elif asset_type == "DeFi Tokens":
            asset_options = {"Chainlink": "LINK-USD", "Aave": "AAVE-USD", "Maker": "MKR-USD", "Lido": "LDO-USD", "Synthetix": "SNX-USD"}
            selected_asset = st.selectbox("Select Asset", list(asset_options.keys()))
            symbol = asset_options[selected_asset]
        elif asset_type == "Stocks":
            asset_options = {"Apple": "AAPL", "Tesla": "TSLA", "Google": "GOOGL", "Microsoft": "MSFT", "Amazon": "AMZN"}
            selected_asset = st.selectbox("Select Asset", list(asset_options.keys()))
            symbol = asset_options[selected_asset]
        elif asset_type == "Forex":
            asset_options = {"EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "USDJPY=X", "AUD/USD": "AUDUSD=X"}
            selected_asset = st.selectbox("Select Asset", list(asset_options.keys()))
            symbol = asset_options[selected_asset]
        else:
            symbol = st.text_input("Enter Symbol (e.g. BTC-USD, AAPL)", "BTC-USD")

    with col_a3:
        period = st.selectbox("Time Period", ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"], index=5)

    # 4. Analyze Button
    if st.button("🚀 Analyze Market Signals"):
        # 5. Analyzing Message & Spinner
        with st.spinner(f"Analyzing {symbol} signals and price action..."):
            interval_map = {"1d": "1m", "5d": "5m", "1mo": "60m", "3mo": "1h", "6mo": "1d", "1y": "1d", "2y": "1d", "5y": "1wk"}
            interval = interval_map.get(period, "1d")
            
            df = api_utils.get_historical_data(symbol, period=period, interval=interval)
            if (df is None or df.empty) and interval != "1d":
                df = api_utils.get_historical_data(symbol, period=period, interval="1d")
                
            if df is not None and not df.empty:
                df = analysis.get_technical_indicators(df)
                signals = analysis.generate_signals(df)
                st.session_state.analysis_result = {"df": df, "signals": signals, "symbol": symbol}
            else:
                st.session_state.analysis_result = "ERROR"

    # Display Results if they exist in session state
    if st.session_state.analysis_result == "ERROR":
        st.error(f"Could not fetch data for {symbol}. Radar sensors are jammed!")
    elif st.session_state.analysis_result is not None:
        res = st.session_state.analysis_result
        df = res['df']
        signals = res['signals']
        
        # Display Charts
        try:
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                               vertical_spacing=0.03, subplot_titles=(f'{res["symbol"]} Price Action', 'Volume'), 
                               row_width=[0.2, 0.7])

            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], 
                                       low=df['Low'], close=df['Close'], name='OHLC'), row=1, col=1)
        
            if 'ma20' in df.columns:
                fig.add_trace(go.Scatter(x=df.index, y=df['ma20'], line=dict(color='yellow', width=1), name='MA20'), row=1, col=1)
            if 'ma50' in df.columns:
                fig.add_trace(go.Scatter(x=df.index, y=df['ma50'], line=dict(color='orange', width=1), name='MA50'), row=1, col=1)
            
            fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume'), row=2, col=1)
            fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, height=500)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Chart Error: {e}")

        # Signal Dashboard
        st.subheader("📡 LiRadar Algo Signals")
        col_s1, col_s2 = st.columns([1, 2])
        
        with col_s1:
            summary_text, summary_type = signals['summary']
            st.markdown(f"""
                <div class="signal-card signal-{summary_type}" style="text-align: center;">
                    <h3>OVERALL SIGNAL</h3>
                    <h1 style="font-size: 2.5rem; margin: 0; color: white;">{summary_text}</h1>
                    <p>Confidence: {signals['strength']}%</p>
                    <hr style="border: 0.5px solid rgba(255,255,255,0.1); margin: 10px 0;">
                    <p style="font-size: 0.85rem; font-style: italic;">{signals['reason']}</p>
                </div>
            """, unsafe_allow_html=True)
            
        with col_s2:
            cols = st.columns(2)
            # Fixed the unpacking to handle 4 values: name, val, desc, s_type
            for i, (name, val, desc, s_type) in enumerate(signals['signals']):
                with cols[i % 2]:
                    st.markdown(f"""
                        <div class="signal-card signal-{s_type}">
                            <div style="display: flex; justify-content: space-between;">
                                <h4 style="margin:0;">{name}</h4>
                                <span style="font-weight: bold;">{val}</span>
                            </div>
                            <p style="font-size: 0.8rem; margin-top: 5px;">{desc}</p>
                        </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("💡 Select an asset and click 'Analyze Market Signals' to start.")

with tab3:
    st.header("Comprehensive Market Overview")
    
    col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
    fng = fetch_fear_and_greed()
    global_data = fetch_global_data()
    
    with col_stats1:
        st.metric("Fear & Greed Index", f"{fng['value']} ({fng['value_classification']})" if fng else "N/A")
    with col_stats2:
        total_mcap = global_data.get("total_market_cap", {}).get("usd", 0)
        st.metric("Total Market Cap", analysis.format_currency(total_mcap))
    with col_stats3:
        btc_dom = global_data.get("market_cap_percentage", {}).get("btc", 0)
        st.metric("BTC Dominance", f"{btc_dom:.1f}%")
    with col_stats4:
        eth_dom = global_data.get("market_cap_percentage", {}).get("eth", 0)
        st.metric("ETH Dominance", f"{eth_dom:.1f}%")

    st.markdown("---")
    
    st.subheader("🚀 Top 10 Cryptocurrencies by Market Cap")
    top_crypto = fetch_top_crypto()
    if top_crypto and isinstance(top_crypto, list) and len(top_crypto) > 0:
        df_crypto = pd.DataFrame(top_crypto)
        st.dataframe(df_crypto[['name', 'symbol', 'current_price', 'market_cap']], hide_index=True, use_container_width=True)
    else:
        st.error("Rate-limited. Please refresh in a moment.")

    st.markdown("---")
    st.subheader("🏦 Top 10 DeFi Protocols by TVL")
    protocols = fetch_defi_protocols()
    if protocols:
        df_p = pd.DataFrame(protocols[:10])
        st.dataframe(df_p[['name', 'tvl', 'chain', 'change_7d']], hide_index=True, use_container_width=True)

# --- Footer & PWA (Safely at bottom) ---
st.markdown("---")
col_f1, col_f2 = st.columns([2, 1])
with col_f1:
    st.markdown(f"🕒 Last updated: **{st.session_state.last_updated}** (UTC)")
with col_f2:
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.session_state.last_updated = datetime.now().strftime("%H:%M:%S")
        st.rerun()

# Defensive PWA injection at the very end
try:
    st.markdown("""
        <link rel="manifest" href="manifest.json">
        <meta name="theme-color" content="#1a1a2e">
        <link rel="apple-touch-icon" href="https://cdn-icons-png.flaticon.com/512/1998/1998664.png">
    """, unsafe_allow_html=True)
except:
    pass
