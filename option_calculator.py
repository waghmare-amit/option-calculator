import streamlit as st

# Apply custom CSS styling for underline (non-bold)
st.markdown("""
    <style>
    .underline {
        text-decoration: underline;
        font-weight: normal;
    }
    </style>
""", unsafe_allow_html=True)

def suggest_option(market_spot, target_level, sl_level, previous_trade=False, profit_loss=None, max_risk=1000, lot_size=75, max_premium=12000):
    delta_reference = {
        "Deep ITM": 0.8,
        "Slight ITM": 0.6,
        "ATM": 0.5,
        "Slight OTM": 0.4,
        "Deep OTM": 0.2
    }

    best_strike = round(market_spot / 50) * 50
    delta = delta_reference["ATM"]
    suggested_type = "ATM"
    actual_sl_points = abs(market_spot - sl_level)
    spot_target_points = abs(market_spot - target_level)

    # Apply Slight ITM if it fits premium range
    estimated_itm_premium = 1.2 * best_strike
    if estimated_itm_premium <= max_premium:
        best_strike -= 50
        delta = delta_reference["Slight ITM"]
        suggested_type = "Slight ITM"

    max_sl_premium = max_risk / lot_size
    max_sl_points = round(max_sl_premium / delta, 2)
    max_sl_points = min(max_sl_points, 30)

    result = {}
    trade_restricted = False

    if previous_trade and profit_loss is not None:
        if profit_loss < 0:
            net_risk = max_risk + profit_loss
            if profit_loss <= -950 or net_risk <= 0:
                st.markdown("<h3 style='color:red; font-weight:bold;'>DON'T TRADE, MAX LOSS FOR THE DAY DONE</h3>", unsafe_allow_html=True)
                trade_restricted = True
            else:
                max_sl_premium = net_risk / lot_size
        else:
            profit_target = 3000 - profit_loss
            if profit_target <= 0:
                st.markdown("<h3 style='color:green; font-weight:bold;'>DON'T TRADE, MAX PROFIT FOR THE DAY HAS BEEN ACHIEVED</h3>", unsafe_allow_html=True)
                return {}
            else:
                target_premium_earned = round(profit_target / lot_size / delta, 2)
                result["<span class='underline'>Target in Premium According to Profit Earned</span>"] = f"<span class='underline'>{target_premium_earned}</span> (in broker, based on earned profit)"

    if not trade_restricted:
        sl_premium = round(max_sl_points * delta, 2)
        estimated_loss = round(sl_premium * lot_size, 2)
        sl_input_premium = round(actual_sl_points * delta, 2)
        target_in_premium = round(spot_target_points * delta, 2)

        risk_status = "Your SL is within the risk limit." if actual_sl_points <= max_sl_points else f"Your SL exceeds your risk limit by {round(actual_sl_points - max_sl_points, 2)} points."

        result.update({
            "<span class='underline'>The Best Strike to Buy</span>": best_strike,
            "Option Type": suggested_type,
            "Expected Delta": delta,
            "<span class='underline'>SL in Charts</span>": f"<span class='underline'>{actual_sl_points}</span> (your input)",
            "<span class='underline'>Max SL Points</span>": f"<span class='underline'>{max_sl_points}</span> (in charts, according to AI calculation for max loss of ₹{round(max_risk, 1)})",
            "<span class='underline'>SL in Premium</span>": f"<span class='underline'>{sl_premium}</span> (in broker, according to AI)",
            "<span class='underline'>SL in Premium Based on SL Input</span>": f"<span class='underline'>{sl_input_premium}</span> (in broker, according to your input SL level)",
            "<span class='underline'>Target in Premium</span>": f"<span class='underline'>{target_in_premium}</span> (in broker, according to your input target level)",
            "<span class='underline'>Estimated Loss</span>": f"<span class='underline'>₹{estimated_loss}</span>",
            "Risk Check": risk_status
        })

    return result

# === UI Starts Here ===
st.title("Option Strike Price Selector")

market_spot = st.number_input("Enter Market Spot Price:", min_value=0.0, format="%.2f")
previous_trade = st.radio("Did you make a previous trade?", ["No", "Yes"]) == "Yes"

profit_loss = None
if previous_trade:
    profit_loss = st.number_input("Enter Profit (+) or Loss (-):", format="%.2f")

target_level = st.number_input("Enter Target Level:", min_value=0.0, format="%.2f")
sl_level = st.number_input("Enter Stop Loss Level:", min_value=0.0, format="%.2f")

if st.button("Calculate Option"):
    if market_spot > 0 and sl_level > 0 and target_level > 0:
        suggestion = suggest_option(
            market_spot, target_level, sl_level,
            previous_trade=previous_trade,
            profit_loss=profit_loss
        )
        if suggestion:
            st.markdown("### Suggested Option:")
            for key, value in suggestion.items():
                if 'underline' in key:
                    st.markdown(f"{key}: {value}", unsafe_allow_html=True)
                else:
                    st.markdown(f"{key}: {value}", unsafe_allow_html=True)
    else:
        st.error("Please enter valid values for all fields.")
