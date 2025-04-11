import streamlit as st

# Apply custom CSS styling for underlining with normal font weight
st.markdown("""
    <style>
    .underline {
        text-decoration: underline;
        font-weight: normal;
    }
    .highlight-red {
        color: red;
        font-weight: bold;
        text-transform: uppercase;
    }
    .highlight-green {
        color: green;
        font-weight: bold;
        text-transform: uppercase;
    }
    </style>
""", unsafe_allow_html=True)

def suggest_option(market_spot, target_level, sl_level, max_risk=1000, lot_size=75, max_premium=12000,
                   prev_trade=False, profit_loss=0.0):
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
    max_sl_points = min(max_sl_points, 40)

    if prev_trade:
        if profit_loss < 0:
            adjusted_risk = max_risk + profit_loss
            if adjusted_risk <= 0:
                st.markdown("<div class='highlight-red'>DON'T TRADE. MAXIMUM LOSS LIMIT FOR THE DAY REACHED.</div>", unsafe_allow_html=True)
                return None
            else:
                max_sl_premium = adjusted_risk / lot_size
        elif profit_loss > 0:
            adjusted_target_profit = 3000 - profit_loss
            if adjusted_target_profit <= 0:
                st.markdown("<div class='highlight-green'>YOU DON'T HAVE TO TRADE ANYMORE, SINCE MAXIMUM PROFIT HAS BEEN ACHIEVED.</div>", unsafe_allow_html=True)

    sl_premium = round(max_sl_points * delta, 2)
    estimated_loss = round(sl_premium * lot_size, 2)
    sl_input_premium = round(actual_sl_points * delta, 2)

    suggested_type = "ATM"
    estimated_itm_premium = 1.2 * best_strike
    if estimated_itm_premium <= max_premium:
        best_strike -= 50
        delta = delta_reference["Slight ITM"]
        suggested_type = "Slight ITM"

    estimated_profit_premium = round(spot_target_points * delta, 2)
    if profit_loss > 0 and profit_loss < 3000:
        estimated_profit_premium = round((3000 - profit_loss) / lot_size, 2)

    if actual_sl_points <= max_sl_points:
        risk_status = f"Your SL is within the risk limit."
    else:
        risk_status = f"Your SL exceeds your risk limit by {round(actual_sl_points - max_sl_points, 2)} points."

    return {
        "<span class='underline'>The Best Strike to Buy</span>": best_strike,
        "Option Type": suggested_type,
        "Expected Delta": delta,
        "<span class='underline'>SL in Charts</span>": f"{actual_sl_points} (your input)",
        "<span class='underline'>Max SL Points</span>": f"{max_sl_points} (in charts, according to AI calculation for max loss of ₹{round(max_sl_premium * lot_size)})",
        "<span class='underline'>SL in Premium</span>": f"{sl_premium} (in broker, according to AI)",
        "<span class='underline'>SL in Premium Based on SL Input</span>": f"{sl_input_premium} (in broker, according to your input SL level)",
        "<span class='underline'>Estimated Loss</span>": f"₹{estimated_loss}",
        "<span class='underline'>Target in Premium</span>": f"{estimated_profit_premium} (in broker, according to your input target level)",
        "Risk Check": risk_status
    }

st.title("Option Strike Price Selector")

market_spot = st.number_input("Enter Market Spot Price:", min_value=0.0, format="%.2f")

previous_trade = st.radio("Were there any previous trades today?", ("No", "Yes"))

profit_loss = 0.0
if previous_trade == "Yes":
    profit_loss = st.number_input("Enter total Profit/Loss from previous trade (use negative for loss):", format="%.2f")

sl_level = st.number_input("Enter Stop Loss Level:", min_value=0.0, format="%.2f")
target_level = st.number_input("Enter Target Level:", min_value=0.0, format="%.2f")

if st.button("Calculate Option"):
    if market_spot > 0 and sl_level > 0 and target_level > 0:
        result = suggest_option(
            market_spot, target_level, sl_level,
            prev_trade=(previous_trade == "Yes"),
            profit_loss=profit_loss
        )
        if result:
            st.markdown("### Suggested Option:")
            for key, value in result.items():
                st.markdown(f"{key}: {value}", unsafe_allow_html=True)
    else:
        st.error("Please enter valid values for all fields.")
