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

# --- Theme Styling ---
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #161b22;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #30363d;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #238636;
        color: white;
        border: none;
    }
    .stButton>button:hover {
        background-color: #2ea043;
    }
    /* Custom style for the chat container */
    .chat-container {
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 20px;
        background-color: #0d1117;
        margin-bottom: 20px;
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
    # Streamlit's chat_input is automatically sticky to the bottom of the screen or container
    if prompt := st.chat_input("Ex: 'Price of Bitcoin' or 'Top DeFi protocols'"):
        # We append to history first so it renders in the loop above on next run
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get response from our logic
        response = bot_logic.get_liradar_response(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Trigger a rerun to show the new messages immediately
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
