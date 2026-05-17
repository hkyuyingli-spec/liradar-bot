import streamlit as st
import bot_logic
import api_utils
import analysis
import pandas as pd
import plotly.express as px

# --- Page Configuration ---
st.set_page_config(
    page_title="LiRadar - DeFi Analysis Bot",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

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

# --- Theme Styling (Professional Dark Trading Dashboard) ---
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
st.title("LiRadar Trading Dashboard")

# Top Metrics Row (Professional Dashboard feel)
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.metric("BTC Price", "$64,231", "1.2%")
with col_m2:
    st.metric("ETH Price", "$3,452", "-0.5%")
with col_m3:
    st.metric("Total DeFi TVL", "$82.4B", "2.1%")
with col_m4:
    st.metric("LiRadar Status", "Online", "v1.2")

# Tabs for different views
tab1, tab2 = st.tabs(["💬 LiRadar Chat", "📈 Market LiRadar"])

with tab1:
    # Chat history at the TOP
    chat_container = st.container()

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Welcome back! LiRadar reporting for duty. How can I assist your portfolio today?"}
        ]

    # Display chat messages from history inside the container
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat bar at the BOTTOM
    if prompt := st.chat_input("Ex: 'Price of Bitcoin' or 'Top DeFi protocols'"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get response from our logic
        response = bot_logic.get_liradar_response(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        st.rerun()

with tab2:
    st.header("DeFi Market Overview")
    st.write("Top 10 DeFi Protocols by TVL")
    
    protocols = api_utils.get_defi_protocols()
    if protocols:
        df = pd.DataFrame(protocols[:10])
        # Clean up data for display
        df_display = df[['name', 'tvl', 'change_7d', 'chain']].copy()
        df_display['tvl_formatted'] = df_display['tvl'].apply(analysis.format_currency)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create a bar chart for TVL
            fig = px.bar(df_display, x='name', y='tvl', 
                         title="Top Protocols by TVL",
                         labels={'tvl': 'Total Value Locked (USD)', 'name': 'Protocol'},
                         template="plotly_dark",
                         color='tvl')
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.dataframe(df_display[['name', 'tvl_formatted', 'change_7d']], 
                         hide_index=True, 
                         use_container_width=True)
            
        st.info("💡 LiRadar Insight: TVL represents the total assets currently being used in the protocol. Higher is generally safer!")
    else:
        st.error("Could not fetch market data. LiRadar sensors are jammed!")
