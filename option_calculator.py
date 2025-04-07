import streamlit as st

def suggest_option(market_spot, target_level, sl_level, max_risk=1000, lot_size=75, max_premium=12000):
    delta_reference = {
        "Deep ITM": 0.8,
        "Slight ITM": 0.6,
        "ATM": 0.5,
        "Slight OTM": 0.4,
        "Deep OTM": 0.2
    }

    actual_sl_points = abs(market_spot - sl_level)
    spot_target_points = abs(market_spot - target_level)

    # Choose ATM strike
    best_strike = round(market_spot / 50) * 50
    delta = delta_reference["ATM"]

    # Calculate max SL points that fit within risk
    max_sl_premium = max_risk / lot_size
    max_sl_points = round(max_sl_premium / delta, 2)
    max_sl_points = min(max_sl_points, 30)  # Ensure SL points do not exceed 30

    sl_premium = round(max_sl_points * delta, 2)
    estimated_loss = round(sl_premium * lot_size, 2)

    suggested_type = "ATM"
    estimated_itm_premium = 1.2 * best_strike
    if estimated_itm_premium <= max_premium:
        best_strike = best_strike - 50
        delta = delta_reference["Slight ITM"]
        suggested_type = "Slight ITM"

    estimated_profit_premium = round(spot_target_points * delta, 2)
    estimated_profit = round(estimated_profit_premium * lot_size, 2)
    risk_reward_ratio = round(estimated_profit / estimated_loss, 2) if estimated_loss > 0 else "N/A"

    breakeven_move = round(sl_premium / delta, 2) if delta > 0 else "N/A"

    # Risk check status
    if actual_sl_points <= max_sl_points:
        risk_status = "✅ Your SL is within the risk limit."
    else:
        risk_status = f"❌ Your SL exceeds your risk limit by {round(actual_sl_points - max_sl_points, 2)} points."

    return {
        "Best Strike to Buy": best_strike,
        "Option Type": suggested_type,
        "Expected Delta": delta,
        "Your SL in Charts": f"{actual_sl_points} (your input)",
        "Max SL Points": f"{max_sl_points} (in charts)",
        "Stop-Loss in Premium": f"{sl_premium} (in broker)",
        "Estimated Loss (₹)": estimated_loss,
        "Estimated Profit in Premium": estimated_profit_premium,
        "Estimated Profit (₹)": estimated_profit,
        "Risk:Reward Ratio": risk_reward_ratio,
        "Breakeven Move (Points)": breakeven_move,
        "Risk Check": risk_status
    }

# Streamlit UI
st.title("Option Strike Price Selector")

market_spot = st.number_input("Enter Market Spot Price:", min_value=0.0, format="%.2f")
sl_level = st.number_input("Enter Stop Loss Level:", min_value=0.0, format="%.2f")
target_level = st.number_input("Enter Target Level:", min_value=0.0, format="%.2f")

if st.button("Calculate Option"):
    if market_spot > 0 and sl_level > 0 and target_level > 0:
        suggestion = suggest_option(market_spot, target_level, sl_level)
        st.write("### Suggested Option:")
        for key, value in suggestion.items():
            st.write(f"**{key}:** {value}")
    else:
        st.error("Please enter valid values for all fields.")
