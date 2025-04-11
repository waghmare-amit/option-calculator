import streamlit as st

# Custom styling
st.markdown("""
    <style>
    .underline {
        text-decoration: underline;
        font-weight: normal;
    }
    .red-alert {
        color: red;
        font-weight: bold;
        text-transform: uppercase;
    }
    .green-alert {
        color: green;
        font-weight: bold;
        text-transform: uppercase;
    }
    </style>
""", unsafe_allow_html=True)

def suggest_option(market_spot, target_level, sl_level, adjusted_max_risk=1000, lot_size=75, max_premium=12000):
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

    max_sl_premium = adjusted_max_risk / lot_size
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

    risk_status = "Your SL is within the risk limit." if actual_sl_points <= max_sl_points else \
        f"Your SL exceeds your risk limit by {round(actual_sl_points - max_sl_points, 2)} points."

    return {
        "<span class='underline'>The Best Strike to Buy</span>": best_strike,
        "Option Type": suggested_type,
        "Expected Delta": delta,
        "<span class='underline'>SL in Charts</span>": f"{actual_sl_points} (in charts, according to AI calculation for max loss of ₹{adjusted_max_risk})",
        "<span class='underline'>Max SL Points</span>": f"{max_sl_points} (in charts, according to AI calculation for max loss of ₹{adjusted_max_risk})",
        "<span class='underline'>SL in Premium</span>": f"{sl_premium} (in broker, according to AI)",
        "<span class='underline'>SL in Premium Based on SL Input</span>": f"{sl_input_premium} (in broker, according to your input sl level)",
        "<span class='underline'>Estimated Loss</span>": f"₹{estimated_loss}",
        "Estimated Profit in Premium": estimated_profit_premium,
    }

def display_results(suggestion, target_premium_custom=None, show_custom_msg=False):
    st.markdown("### Suggested Option:")
    for key, value in suggestion.items():
        st.markdown(f"{key}: {value}", unsafe_allow_html=True)

    if target_premium_custom is not None:
        st.markdown(f"<span class='underline'>Target Points in Premium</span>: {target_premium_custom} (in broker, according to your input target level)", unsafe_allow_html=True)
    else:
        st.markdown(f"<span class='underline'>Target Points in Premium</span>: {suggestion['Estimated Profit in Premium']} (in broker, according to your input target level)", unsafe_allow_html=True)

    if show_custom_msg:
        st.markdown(f"<div class='green-alert'>YOU DON'T HAVE TO TRADE ANYMORE, SINCE MAX PROFIT HAS BEEN ACHIEVED.</div>", unsafe_allow_html=True)

# Streamlit layout
st.title("Option Strike Price Selector")

market_spot = st.number_input("Enter Market Spot Price:", min_value=0.0, format="%.2f")

prev_trade = st.radio("Did you make a previous trade?", ["No", "Yes"])

if prev_trade == "No":
    target_level = st.number_input("Enter Target Level:", min_value=0.0, format="%.2f")
    sl_level = st.number_input("Enter Stop Loss Level:", min_value=0.0, format="%.2f")
    if st.button("Calculate Option"):
        if market_spot > 0 and sl_level > 0 and target_level > 0:
            suggestion = suggest_option(market_spot, target_level, sl_level)
            display_results(suggestion)
        else:
            st.error("Please enter valid values for all fields.")

elif prev_trade == "Yes":
    pl_input = st.number_input("Enter Profit (positive) or Loss (negative):", format="%.2f")
    if pl_input < 0:
        adjusted_risk = 1000 - abs(pl_input)
        if abs(pl_input) >= 950 or adjusted_risk <= 0:
            st.markdown("<div class='red-alert'>DON'T TRADE. MAXIMUM LOSS LIMIT FOR THE DAY REACHED.</div>", unsafe_allow_html=True)
        else:
            target_level = st.number_input("Enter Target Level:", min_value=0.0, format="%.2f")
            sl_level = st.number_input("Enter Stop Loss Level:", min_value=0.0, format="%.2f")
            if st.button("Calculate Option"):
                suggestion = suggest_option(market_spot, target_level, sl_level, adjusted_max_risk=adjusted_risk)
                display_results(suggestion)
    else:
        remaining_profit_room = 3000 - pl_input
        target_level = st.number_input("Enter Target Level:", min_value=0.0, format="%.2f")
        sl_level = st.number_input("Enter Stop Loss Level:", min_value=0.0, format="%.2f")
        if st.button("Calculate Option"):
            suggestion = suggest_option(market_spot, target_level, sl_level)
            if remaining_profit_room <= 0:
                display_results(suggestion, show_custom_msg=True)
            else:
                target_custom_premium = round(remaining_profit_room / 75, 2)
                display_results(suggestion, target_premium_custom=target_custom_premium)
