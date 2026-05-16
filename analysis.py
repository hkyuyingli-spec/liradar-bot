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
