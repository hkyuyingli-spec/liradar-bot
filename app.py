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

# --- Auto-Refresh Logic ---
REFRESH_INTERVAL = 60 # seconds

if "last_updated" not in st.session_state:
    st.session_state.last_updated = datetime.now().strftime("%H:%M:%S")

# --- PWA Injection ---
pwa_html = """
    <link rel="manifest" href="./manifest.json">
    <meta name="theme-color" content="#1a1a2e">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <link rel="apple-touch-icon" href="https://cdn-icons-png.flaticon.com/512/1998/1998664.png">
    
    <script>
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', function() {
                navigator.serviceWorker.register('./service-worker.js').then(function(registration) {
                    console.log('ServiceWorker registration successful with scope: ', registration.scope);
                }, function(err) {
                    console.log('ServiceWorker registration failed: ', err);
                });
            });
        }
    </script>
"""
st.markdown(pwa_html, unsafe_allow_html=True)

# --- Theme Styling ---
st.markdown("""
    <style>
    /* Global Background and Text */
    .stApp {
        background-color: #1a1a2e;
        color: #ffffff;
    }
    
    /* Main Content Area */
    .main {
        background-color: #1a1a2e;
    }

    /* Metric Cards Styling */
    [data-testid="stMetric"] {
        background-color: #0f3460;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #16213e;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    /* Metric Label (Titles) */
    [data-testid="stMetricLabel"] {
        color: #e0e0e0 !important;
        font-weight: 500;
    }
    
    /* Metric Value (Numbers) */
    [data-testid="stMetricValue"] {
        color: #f1c40f !important; /* High-contrast Yellow */
        font-weight: 800 !important;
        font-size: 1.8rem !important;
    }

    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        background-color: #e94560; /* Vibrant accent color */
        color: white;
        border: none;
        font-weight: bold;
        font-size: 1rem;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #ff4d6d;
        transform: translateY(-2px);
    }

    /* Signal Cards */
    .signal-card {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border: 1px solid #30363d;
    }
    .signal-success { background-color: rgba(40, 167, 69, 0.2); border-color: #28a745; border-left: 5px solid #28a745; }
    .signal-danger { background-color: rgba(220, 53, 69, 0.2); border-color: #dc3545; border-left: 5px solid #dc3545; }
    .signal-warning { background-color: rgba(255, 193, 7, 0.1); border-color: #ffc107; border-left: 5px solid #ffc107; }

    /* Chat Messages Visibility */
    [data-testid="stChatMessage"] {
        background-color: #16213e;
        border: 1px solid #0f3460;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #16213e;
    }
    
    /* Custom style for the chat container */
    .chat-container {
        border: 1px solid #16213e;
        border-radius: 10px;
        padding: 15px;
        background-color: #1a1a2e;
        margin-bottom: 20px;
    }

    /* Mobile optimization for font sizes */
    @media (max-width: 640px) {
        .stMetric {
            margin-bottom: 15px;
        }
        h1 {
            font-size: 1.5rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

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

# Tabs at the TOP (Directly below header)
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

    # Map periods to intervals for better chart resolution
    interval_map = {
        "1d": "1m",
        "5d": "5m",
        "1mo": "60m",
        "3mo": "1h",
        "6mo": "1d",
        "1y": "1d",
        "2y": "1d",
        "5y": "1wk"
    }
    interval = interval_map.get(period, "1d")

    # Fetch Data
    with st.spinner(f"Fetching historical data for {symbol} ({period})..."):
        df = api_utils.get_historical_data(symbol, period=period, interval=interval)
        
        # Fallback to daily interval if more granular data fails
        if (df is None or df.empty) and interval != "1d":
            df = api_utils.get_historical_data(symbol, period=period, interval="1d")
    
    if df is not None and not df.empty and len(df) > 0:
        # Calculate Indicators
        df = analysis.get_technical_indicators(df)
        signals = analysis.generate_signals(df)
        
        # Display Charts
        try:
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                               vertical_spacing=0.03, subplot_titles=(f'{symbol} Price Action', 'Volume'), 
                               row_width=[0.2, 0.7])

            # Candlestick (Always added if df exists)
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], 
                                       low=df['Low'], close=df['Close'], name='OHLC'), row=1, col=1)
        
            # Moving Averages (Added only if data exists)
            if 'ma20' in df.columns and not df['ma20'].isna().all():
                fig.add_trace(go.Scatter(x=df.index, y=df['ma20'], line=dict(color='yellow', width=1), name='MA20'), row=1, col=1)
            if 'ma50' in df.columns and not df['ma50'].isna().all():
                fig.add_trace(go.Scatter(x=df.index, y=df['ma50'], line=dict(color='orange', width=1), name='MA50'), row=1, col=1)
            if 'ma200' in df.columns and not df['ma200'].isna().all():
                fig.add_trace(go.Scatter(x=df.index, y=df['ma200'], line=dict(color='red', width=1), name='MA200'), row=1, col=1)

            # Bollinger Bands (Added only if data exists)
            if 'bb_h' in df.columns and not df['bb_h'].isna().all():
                fig.add_trace(go.Scatter(x=df.index, y=df['bb_h'], line=dict(color='gray', width=1, dash='dash'), name='BB Upper'), row=1, col=1)
            if 'bb_l' in df.columns and not df['bb_l'].isna().all():
                fig.add_trace(go.Scatter(x=df.index, y=df['bb_l'], line=dict(color='gray', width=1, dash='dash'), name='BB Lower'), row=1, col=1)

            # Volume
            fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume'), row=2, col=1)

            fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, height=600)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error generating chart: {e}")

        # Signal Dashboard
        st.subheader("📡 LiRadar Algo Signals")
        col_s1, col_s2 = st.columns([1, 2])
        
        with col_s1:
            summary_text, summary_type = signals['summary']
            st.markdown(f"""
                <div class="signal-card signal-{summary_type}" style="text-align: center;">
                    <h3>OVERALL SIGNAL</h3>
                    <h1 style="font-size: 2.5rem; margin: 0; color: white;">{summary_text}</h1>
                    <p style="margin-top:10px;"><b>Confidence:</b> {signals['strength']}%</p>
                    <hr style="border: 0.5px solid rgba(255,255,255,0.1); margin: 15px 0;">
                    <p style="font-size: 0.9rem; font-style: italic;">{signals['reason']}</p>
                </div>
            """, unsafe_allow_html=True)
            
        with col_s2:
            st.write("#### Detailed Technical Insights")
            cols = st.columns(2)
            for i, (name, val, desc, s_type) in enumerate(signals['signals']):
                with cols[i % 2]:
                    st.markdown(f"""
                        <div class="signal-card signal-{s_type}">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <h4 style="margin:0;">{name}</h4>
                                <span style="font-weight: bold; font-size: 1.1rem;">{val}</span>
                            </div>
                            <p style="margin-top:10px; font-size: 0.85rem; line-height: 1.4;">{desc}</p>
                        </div>
                    """, unsafe_allow_html=True)
    else:
        st.error(f"Could not fetch data for {symbol}. Please check the symbol and try again.")

with tab3:
    st.header("Comprehensive Market Overview")
    
    # 1. Market Sentiment & Stats Row
    col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
    
    fng = api_utils.get_fear_and_greed_index()
    global_data = api_utils.get_global_market_data()
    
    with col_stats1:
        if fng:
            st.metric("Fear & Greed Index", f"{fng['value']} ({fng['value_classification']})")
        else:
            st.metric("Fear & Greed Index", "N/A")
            
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
    
    # 2. Top 10 Cryptocurrencies Section
    st.subheader("🚀 Top 10 Cryptocurrencies by Market Cap")
    top_crypto = api_utils.get_top_crypto_prices()
    
    # PROBLEM 1 FIX: Ensure top_crypto is a list and handle mapping correctly
    if top_crypto and isinstance(top_crypto, list):
        # CoinGecko sometimes returns a dictionary with an 'error' key if rate limited
        if len(top_crypto) > 0 and isinstance(top_crypto[0], dict) and 'id' in top_crypto[0]:
            df_crypto = pd.DataFrame(top_crypto)
            
            # Map columns and ensure they exist
            cols_map = {
                'name': 'Name',
                'symbol': 'Symbol',
                'current_price': 'Price (USD)',
                'price_change_percentage_24h': '24h Change (%)',
                'market_cap': 'Market Cap'
            }
            
            # Filter to columns that actually exist in the API response
            existing_cols = [c for c in cols_map.keys() if c in df_crypto.columns]
            
            if len(existing_cols) > 0:
                df_display_final = df_crypto[existing_cols].copy()
                
                # Format for display
                if 'symbol' in df_display_final.columns:
                    df_display_final['symbol'] = df_display_final['symbol'].str.upper()
                
                if 'current_price' in df_display_final.columns:
                    df_display_final['current_price'] = df_display_final['current_price'].apply(
                        lambda x: f"${x:,.2f}" if x >= 1 else f"${x:.6f}"
                    )
                
                if 'price_change_percentage_24h' in df_display_final.columns:
                    df_display_final['price_change_percentage_24h'] = df_display_final['price_change_percentage_24h'].apply(
                        lambda x: f"{x:+.2f}%" if pd.notnull(x) else "0.00%"
                    )
                
                if 'market_cap' in df_display_final.columns:
                    df_display_final['market_cap'] = df_display_final['market_cap'].apply(analysis.format_currency)
                
                # Rename columns for final table
                df_display_final.columns = [cols_map[c] for c in existing_cols]
                
                st.dataframe(df_display_final, hide_index=True, use_container_width=True)
            else:
                st.warning("⚠️ Market data columns are currently unavailable. Radar is retrying...")
        else:
            st.error("📡 LiRadar sensors are temporarily rate-limited by CoinGecko. Please wait a minute.")
    else:
        st.error("Could not fetch top crypto prices. Check your connection or try again later.")

    st.markdown("---")

    # 3. Top DeFi Protocols Section
    st.subheader("🏦 Top 10 DeFi Protocols by TVL")
    protocols = api_utils.get_defi_protocols()
    if protocols and isinstance(protocols, list):
        df_p = pd.DataFrame(protocols[:10])
        
        # Ensure required columns exist
        required_p_cols = ['name', 'tvl', 'change_7d', 'chain']
        existing_p_cols = [c for c in required_p_cols if c in df_p.columns]
        
        if len(existing_p_cols) >= 2:
            df_display_p = df_p[existing_p_cols].copy()
            df_display_p['TVL'] = df_display_p['tvl'].apply(analysis.format_currency)
            
            col_dash1, col_dash2 = st.columns([2, 1])
            
            with col_dash1:
                fig_p = px.bar(df_display_p, x='name', y='tvl', 
                             title="Top Protocols by TVL",
                             labels={'tvl': 'Total Value Locked (USD)', 'name': 'Protocol'},
                             template="plotly_dark",
                             color='tvl')
                st.plotly_chart(fig_p, use_container_width=True)
                
            with col_dash2:
                # Rename for cleaner table
                st.dataframe(df_display_p[['name', 'TVL', 'change_7d']], 
                             hide_index=True, 
                             use_container_width=True)
                
            st.info("💡 LiRadar Insight: TVL represents the total assets currently being used in the protocol. Higher is generally safer!")
        else:
            st.warning("DeFi data structure not as expected. Scanning for updates...")
    else:
        st.error("Could not fetch DeFi protocols data. LiRadar sensors are jammed!")

# --- Auto-Refresh Footer ---
st.markdown("---")
col_f1, col_f2, col_f3 = st.columns([1, 1, 1])

with col_f1:
    st.write(f"🕒 Last updated: **{st.session_state.last_updated}**")

with col_f2:
    if st.button("🔄 Refresh Data Now"):
        st.session_state.last_updated = datetime.now().strftime("%H:%M:%S")
        st.rerun()

with col_f3:
    countdown_placeholder = st.empty()

# --- Countdown Logic ---
for i in range(REFRESH_INTERVAL, 0, -1):
    countdown_placeholder.write(f"⏱️ Next update in: **{i}s**")
    time.sleep(1)

# Update timestamp and rerun
st.session_state.last_updated = datetime.now().strftime("%H:%M:%S")
st.rerun()
