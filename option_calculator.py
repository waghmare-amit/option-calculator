import streamlit as st

# Apply custom CSS styling
st.markdown("""
    <style>
    .underline {
        text-decoration: underline;
        font-weight: normal;
    }
    .no-underline {
        text-decoration: none;
        font-weight: normal;
    }
    </style>
""", unsafe_allow_html=True)

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

    best_strike = round(market_spot / 50) * 50
    delta = delta_reference["ATM"]

    max_sl_premium = max_risk / lot_size
    max_sl_points = round(max_sl_premium / delta, 2)
    max_sl_points = min(max_sl_points, 30)

    sl_premium = round(max_sl_points * delta, 2)
    estimated_loss = round(sl_premium * lot_size, 2)

    sl_input_premium = round(actual_sl_points * delta, 2)

    suggested_type = "ATM"
    estimated_itm_premium = 1.2 * best_strike
    if estimated_itm_premium <= max_premium:
        best_strike = best_strike - 50
        delta = delta_reference["Slight ITM"]
        suggested_type = "Slight ITM"

    estimated_profit_premium = round(spot_target_points * delta, 2)
    estimated_profit_total = round(estimated_profit_premium * lot_size, 2)

    if actual_sl_points <= max_sl_points:
        risk_status = f"Your SL is within the risk limit."
    else:
        risk_status = f"Your SL exceeds your risk limit by {round(actual_sl_points - max_sl_points, 2)} points."

    return {
        "<span class='underline'>The Best Strike to Buy</span>": best_strike,
        "Option Type": suggested_type,
        "Expected Delta": delta,
        "<span class='underline'>SL in Charts</span>": f"<span class='no-underline'>{actual_sl_points}</span>",
        "<span class='underline'>Max SL Points</span>": f"<span class='no-underline'>{max_sl_points}</span>",
        "<span class='underline'>SL in Premium</span>": f"<span class='no-underline'>{sl_premium}</span>",
        "<span class='underline'>SL in Premium Based on SL Input</span>": f"<span class='no-underline'>{sl_input_premium}</span>",
        "<span class='underline'>Estimated Loss</span>": f"<span class='no-underline'>₹{estimated_loss}</span>",
        "<span class='underline'>Estimated Profit in Premium</span>": f"<span class='no-underline'>{estimated_profit_premium}</span>",
        "<span class='underline'>Estimated Profit (Total)</span>": f"<span class='no-underline'>₹{estimated_profit_total}</span>",
        "Risk Check": risk_status
    }

st.title("Option Strike Price Selector")

market_spot = st.number_input("Enter Market Spot Price:", min_value=0.0, format="%.2f")
sl_level = st.number_input("Enter Stop Loss Level:", min_value=0.0, format="%.2f")
target_level = st.number_input("Enter Target Level:", min_value=0.0, format="%.2f")

if st.button("Calculate Option"):
    if market_spot > 0 and sl_level > 0 and target_level > 0:
        suggestion = suggest_option(market_spot, target_level, sl_level)
        st.markdown("### Suggested Option:")
        for key, value in suggestion.items():
            st.markdown(f"{key}: {value}", unsafe_allow_html=True)
    else:
        st.error("Please enter valid values for all fields.")
