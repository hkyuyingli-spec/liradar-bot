import api_utils
import analysis
import pandas as pd

def get_liradar_response(prompt):
    """The brain of LiRadar. Interprets user input and returns a response."""
    prompt = prompt.lower()
    
    # 1. Price Check
    if "price" in prompt or "how much is" in prompt:
        # Remove common punctuation to better identify token names
        clean_prompt = prompt.replace("?", "").replace("!", "").replace(".", "").replace(",", "")
        words = clean_prompt.split()
        for word in words:
            # Basic filter to find potential token names
            if word not in ["price", "how", "much", "is", "of", "the", "what"]:
                token_id = api_utils.search_token_id(word)
                if token_id:
                    data = api_utils.get_token_price(token_id)
                    if data:
                        price = data.get("usd")
                        change = data.get("usd_24h_change", 0)
                        trend = "📈" if change > 0 else "📉"
                        return f"LiRadar here. **{word.upper()}** is currently trading at **${price:,.2f}**. {trend} That's a **{change:.2f}%** change in the last 24 hours. A solid observation!"
        return "I couldn't find the price for that specific token. Are you sure you spelled it right? I'm scanning all major exchanges."

    # 2. Protocol Rankings / TVL
    elif "ranking" in prompt or "top protocol" in prompt or "tvl" in prompt:
        protocols = api_utils.get_defi_protocols()
        if protocols:
            top_5 = protocols[:5]
            response = "Scanning the DeFi landscape... Here are the top 5 protocols by Total Value Locked (TVL):\n\n"
            for i, p in enumerate(top_5, 1):
                tvl = analysis.format_currency(p.get('tvl', 0))
                response += f"{i}. **{p['name']}** - {tvl} ({p.get('change_7d', 0):.2f}% 7d change)\n"
            return response + "\nTVL is a great indicator of trust and liquidity in a protocol."

    # 3. Yield / Returns
    elif "yield" in prompt or "calculate" in prompt or "return" in prompt:
        return "I see you're looking for returns! To calculate your potential yield, tell me: 'Calculate yield for $1000 at 10% for 30 days'. I'll crunch the numbers for you."

    # 4. Market Trends
    elif "trend" in prompt or "market" in prompt:
        return "The market is showing interesting activity. Most DeFi protocols are focusing on Layer 2 scaling right now. Keep an eye on Arbitrum and Optimism for the next wave of liquidity!"

    # 5. Default Response
    else:
        return ("LiRadar reporting for duty! I can help you with:\n"
                "- **Price checks** (e.g., 'Price of Ethereum')\n"
                "- **DeFi Rankings** (e.g., 'Show me top protocols')\n"
                "- **TVL Analysis** (e.g., 'What is the TVL of Uniswap?')\n"
                "- **Yield Calculations** (Coming soon in full detail!)\n\n"
                "How can I assist your portfolio today?")

def process_yield_command(principal, apr, days):
    """Calculates returns and returns a formatted string."""
    results = analysis.calculate_yield(principal, apr, days)
    return (f"Calculation complete. If you invest **${principal:,.2f}** at **{apr}% APR** for **{days} days**:\n\n"
            f"- **Simple Return**: ${results['simple_return']:,.2f}\n"
            f"- **Compound Return**: ${results['compound_return']:,.2f} (Daily compounding)\n\n"
            "Remember, in DeFi, high yields often come with higher risks like impermanent loss!")
