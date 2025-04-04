import streamlit as st

# Set page to wide mode for better mobile display
st.set_page_config(layout="wide")

def suggest_option(market_spot, target_level, sl_level, max_risk=1000, lot_size=75, max_premium=12000):
    delta_reference = {
        "Deep ITM": 0.8,
        "Slight ITM": 0.6,
        "ATM": 0.5,
        "Slight OTM": 0.4,
        "Deep OTM": 0.2
    }
    
    spot_sl_points = abs(market_spot - sl_level)
    spot_target_points = abs(market_spot - target_level)
    
    # Choose ATM strike
    best_strike = round(market_spot / 50) * 50
    delta = delta_reference["ATM"]
    
    # Calculate max SL points that fit within risk
    max_sl_premium = max_risk / lot_size
    max_sl_points = round(max_sl_premium / delta, 2)
    max_sl_points = min(max_sl_points, 30)  # Ensure SL points do not exceed 30
    
    # Convert SL points to actual premium movement
    sl_premium = round(max_sl_points * delta, 2)
    estimated_loss = round(sl_premium * lot_size, 2)

    # Determine if ITM is viable (checking estimated price within budget)
    suggested_type = "ATM"
    estimated_itm_premium = 1.2 * best_strike  # Approx ITM premium estimation
    if estimated_itm_premium <= max_premium:
        best_strike = best_strike - 50  # Move to ITM
        delta = delta_reference["Slight ITM"]
        suggested_type = "Slight ITM"
    
    estimated_profit_premium = round(spot_target_points * delta, 2)

    return {
        "Best Strike to Buy": best_strike,
        "Option Type": suggested_type,
        "Expected Delta": delta,
        "Max SL Points": f"{max_sl_points} (in charts)",
        "Stop-Loss in Premium": f"{sl_premium} (in broker)",
        "Estimated Loss (₹)": estimated_loss,
        "Estimated Profit in Premium": estimated_profit_premium
    }

# Streamlit UI
st.title("📊 Option Strike Price Selector")

# Apply custom CSS for better mobile viewing
st.markdown(
    """
    <style>
        body { font-size:18px !important; }
        .stButton>button { font-size: 18px; padding: 10px; }
    </style>
    """,
    unsafe_allow_html=True
)

# Use columns for better spacing
col1, col2 = st.columns([1, 1])

with col1:
    market_spot = st.number_input("Enter Market Spot Price:", min_value=0.0, format="%.2f")
    sl_level = st.number_input("Enter Stop Loss Level:", min_value=0.0, format="%.2f")

with col2:
    target_level = st.number_input("Enter Target Level:", min_value=0.0, format="%.2f")

if st.button("Calculate Option"):
    if market_spot > 0 and sl_level > 0 and target_level > 0:
        suggestion = suggest_option(market_spot, target_level, sl_level)
        st.write("### Suggested Option:")
        for key, value in suggestion.items():
            st.write(f"**{key}:** {value}")
    else:
        st.error("Please enter valid values for all fields.")
