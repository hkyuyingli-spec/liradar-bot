import pandas as pd
import ta

def calculate_yield(principal, apr, days):
    """
    Calculate simple and compound yield.
    principal: Initial investment in USD
    apr: Annual Percentage Rate in %
    days: Duration of investment in days
    """
    # Simple Interest
    simple_interest = (principal * (apr / 100) * (days / 365))
    total_simple = principal + simple_interest
    
    # Compound Interest (assuming daily compounding for APY comparison)
    # APY = (1 + r/n)^n - 1
    daily_rate = (apr / 100) / 365
    total_compound = principal * ((1 + daily_rate) ** days)
    compound_interest = total_compound - principal
    
    return {
        "simple_return": round(simple_interest, 2),
        "total_simple": round(total_simple, 2),
        "compound_return": round(compound_interest, 2),
        "total_compound": round(total_compound, 2)
    }

def format_currency(value):
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    return f"${value:,.2f}"

def get_technical_indicators(df):
    """Calculate technical indicators using ta library."""
    if df is None or df.empty:
        return None
    
    # RSI
    try:
        df['rsi'] = ta.momentum.RSIIndicator(df['Close']).rsi()
    except:
        df['rsi'] = pd.NA
    
    # MACD
    try:
        macd = ta.trend.MACD(df['Close'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_diff'] = macd.macd_diff()
    except:
        df['macd'] = df['macd_signal'] = df['macd_diff'] = pd.NA
    
    # Moving Averages
    try:
        df['ma20'] = ta.trend.sma_indicator(df['Close'], window=20)
    except:
        df['ma20'] = pd.NA
        
    try:
        df['ma50'] = ta.trend.sma_indicator(df['Close'], window=50)
    except:
        df['ma50'] = pd.NA
        
    try:
        df['ma200'] = ta.trend.sma_indicator(df['Close'], window=200)
    except:
        df['ma200'] = pd.NA
    
    # Bollinger Bands
    try:
        bb = ta.volatility.BollingerBands(df['Close'])
        df['bb_h'] = bb.bollinger_hband()
        df['bb_l'] = bb.bollinger_lband()
        df['bb_m'] = bb.bollinger_mavg()
    except:
        df['bb_h'] = df['bb_l'] = df['bb_m'] = pd.NA
    
    return df

def generate_signals(df):
    """Generate trading signals based on technical indicators."""
    if df is None or df.empty:
        return None
    
    last_row = df.iloc[-1]
    prev_row = df.iloc[-2] if len(df) > 1 else last_row
    
    signals = []
    strength = 0
    
    # RSI Signals
    if 'rsi' in last_row and not pd.isna(last_row['rsi']):
        rsi_val = round(last_row['rsi'], 2)
        if rsi_val < 30:
            signals.append(("RSI", f"BUY", f"RSI is {rsi_val} - Asset is OVERSOLD - Consider BUYING", "success"))
            strength += 25
        elif rsi_val > 70:
            signals.append(("RSI", f"SELL", f"RSI is {rsi_val} - Asset is OVERBOUGHT - Consider SELLING", "danger"))
            strength -= 25
        else:
            signals.append(("RSI", f"NEUTRAL", f"RSI is {rsi_val} - Market is in neutral territory.", "warning"))
    else:
        signals.append(("RSI", "N/A", "Insufficient data to calculate RSI.", "warning"))
        
    # MACD Signals
    if 'macd' in last_row and not pd.isna(last_row['macd']) and not pd.isna(last_row['macd_signal']):
        if last_row['macd'] > last_row['macd_signal'] and prev_row['macd'] <= prev_row['macd_signal']:
            signals.append(("MACD", "BUY", "MACD shows BULLISH crossover - Momentum is turning positive.", "success"))
            strength += 25
        elif last_row['macd'] < last_row['macd_signal'] and prev_row['macd'] >= prev_row['macd_signal']:
            signals.append(("MACD", "SELL", "MACD shows BEARISH crossover - Trend is turning negative.", "danger"))
            strength -= 25
        else:
            signals.append(("MACD", "NEUTRAL", "MACD is neutral - No clear momentum shift.", "warning"))
    else:
        signals.append(("MACD", "N/A", "Insufficient data to calculate MACD.", "warning"))
        
    # Moving Average Signals
    if 'ma50' in last_row and 'ma200' in last_row and not pd.isna(last_row['ma50']) and not pd.isna(last_row['ma200']):
        if last_row['ma50'] > last_row['ma200'] and prev_row['ma50'] <= prev_row['ma200']:
            signals.append(("MA", "BUY", "Golden Cross detected! MA50 crossed above MA200 - Strong Bullish sign.", "success"))
            strength += 50
        elif last_row['ma50'] < last_row['ma200'] and prev_row['ma50'] >= prev_row['ma200']:
            signals.append(("MA", "SELL", "Death Cross detected! MA50 crossed below MA200 - Strong Bearish sign.", "danger"))
            strength -= 50
        elif last_row['Close'] > last_row['ma200']:
            signals.append(("MA", "BULLISH", "Price is above MA200 - Long term trend is UP.", "success"))
            strength += 10
        else:
            signals.append(("MA", "BEARISH", "Price is below MA200 - Long term trend is DOWN.", "danger"))
            strength -= 10
    elif 'ma50' in last_row and not pd.isna(last_row['ma50']):
         if last_row['Close'] > last_row['ma50']:
            signals.append(("MA", "BULLISH", "Price is above MA50 - Medium term trend is UP.", "success"))
            strength += 10
         else:
            signals.append(("MA", "BEARISH", "Price is below MA50 - Medium term trend is DOWN.", "danger"))
            strength -= 10
    else:
        signals.append(("MA", "N/A", "Insufficient data for Moving Averages.", "warning"))
        
    # Bollinger Bands Signals
    if 'bb_l' in last_row and not pd.isna(last_row['bb_l']) and not pd.isna(last_row['bb_h']):
        if last_row['Close'] < last_row['bb_l']:
            signals.append(("BB", "BUY", "Price hit Lower Bollinger Band - Potential bounce expected.", "success"))
            strength += 15
        elif last_row['Close'] > last_row['bb_h']:
            signals.append(("BB", "SELL", "Price hit Upper Bollinger Band - Asset might be overextended.", "danger"))
            strength -= 15
        else:
            signals.append(("BB", "NEUTRAL", "Price is inside Bollinger Bands - No volatility breakout.", "warning"))
    else:
        signals.append(("BB", "N/A", "Insufficient data for Bollinger Bands.", "warning"))
        
    # Overall Summary
    reason = "Market indicators are mostly balanced."
    if strength >= 50:
        summary = ("STRONG BUY", "success")
        reason = "Multiple technical indicators suggest a powerful upward trend."
    elif strength > 10:
        summary = ("BUY", "success")
        reason = "Technical signals are leaning towards a positive entry point."
    elif strength < -50:
        summary = ("STRONG SELL", "danger")
        reason = "Multiple technical indicators suggest a sharp downward trend."
    elif strength < -10:
        summary = ("SELL", "danger")
        reason = "Technical signals suggest caution as momentum is turning negative."
    else:
        summary = ("NEUTRAL", "warning")
        
    return {
        "signals": signals,
        "summary": summary,
        "reason": reason,
        "strength": abs(strength)
    }
