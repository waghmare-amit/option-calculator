import streamlit as st

# Custom CSS
st.markdown("""
    <style>
    .underline {
        text-decoration: underline;
        font-weight: normal;
    }
    .bold-red {
        color: red;
        font-weight: bold;
        text-transform: uppercase;
    }
    .bold-green {
        color: green;
        font-weight: bold;
        text-transform: uppercase;
    }
    </style>
""", unsafe_allow_html=True)

def suggest_option(market_spot, target_level, sl_level, previous_trade, profit_or_loss, max_risk=1000, lot_size=75, max_premium=12000):
    delta_reference = {
        "Deep ITM": 0.8,
        "Slight ITM": 0.6,
        "ATM": 0.5,
        "Slight OTM": 0.4,
        "Deep OTM": 0.2
    }

    display_message = ""
    show_outputs = True
    delta = delta_reference["ATM"]

    if previous_trade:
        if profit_or_loss < 0:
            adjusted_risk = max_risk + profit_or_loss
            if abs(profit_or_loss) > 950 or adjusted_risk <= 0:
                display_message = "<p class='bold-red'>DON'T TRADE. MAX LOSS FOR THE DAY REACHED.</p>"
                return {"message": display_message}
            else:
                max_risk = adjusted_risk
        else:
            adjusted_profit = 3000 - profit_or_loss
            if adjusted_profit <= 0:
                display_message = "<p class='bold-green'>YOU DON'T HAVE TO TRADE ANYMORE, SINCE MAX PROFIT HAS BEEN ACHIEVED.</p>"
                trade_in_premium = round(adjusted_profit * delta, 2)
                return {
                    "message": display_message,
                    "Trade in Premium according to profit earned": trade_in_premium
                }
            else:
                trade_in_premium = round(adjusted_profit * delta, 2)

    actual_sl_points = abs(market_spot - sl_level)
    spot_target_points = abs(market_spot - target_level)

    best_strike = round(market_spot / 50) * 50

    max_sl_premium = max_risk / lot_size
    max_sl_points = round(max_sl_premium / delta, 2)
    max_sl_points = min(max_sl_points, 30)

    sl_premium = round(max_sl_points * delta, 2)
    estimated_loss = round(sl_premium * lot_size, 2)
    sl_input_premium = round(actual_sl_points * delta, 2)
    estimated_profit_premium = round(spot_target_points * delta, 2)

    if previous_trade and profit_or_loss > 0 and adjusted_profit > 0:
        estimated_profit_premium = round(adjusted_profit * delta, 2)

    suggested_type = "ATM"
    estimated_itm_premium = 1.2 * best_strike
    if estimated_itm_premium <= max_premium:
        best_strike = best_strike - 50
        delta = delta_reference["Slight ITM"]
        suggested_type = "Slight ITM"

    if actual_sl_points <= max_sl_points:
        risk_status = f"Your SL is within the risk limit."
    else:
        risk_status = f"Your SL exceeds your risk limit by {round(actual_sl_points - max_sl_points, 2)} points."

    outputs = {
        "message": display_message if display_message else "",
        "<span class='underline'>The Best Strike to Buy</span>": best_strike,
        "Option Type": suggested_type,
        "Expected Delta": delta,
        "<span class='underline'>SL in Charts</span>": f"{actual_sl_points} (your input)",
        "<span class='underline'>Max SL Points</span>": f"{max_sl_points} (in charts, according to AI calculation for max loss of ₹{max_risk})",
        "<span class='underline'>SL in Premium</span>": f"{sl_premium} (in broker, according to AI)",
        "<span class='underline'>SL in Premium Based on SL Input</span>": f"{sl_input_premium} (in broker, according to your input sl level)",
        "<span class='underline'>Estimated Loss</span>": f"₹{estimated_loss}",
        "Estimated Profit in Premium": f"{estimated_profit_premium} (in broker, according to your input target level)" if not (previous_trade and profit_or_loss > 0 and adjusted_profit > 0) else "",
        "Trade in Premium according to profit earned": trade_in_premium if previous_trade and profit_or_loss > 0 and adjusted_profit > 0 else "",
        "Risk Check": risk_status
    }

    return outputs

# Title
st.title("Option Strike Price Selector")

# Inputs
market_spot = st.number_input("Enter Market Spot Price:", min_value=0.0, format="%.2f")
previous_trade = st.radio("Did you take a previous trade?", ("No", "Yes")) == "Yes"
profit_or_loss = 0

if previous_trade:
    profit_or_loss = st.number_input("Enter profit/loss from previous trade (negative for loss):", format="%.2f")

target_level = st.number_input("Enter Target Level:", min_value=0.0, format="%.2f")
sl_level = st.number_input("Enter Stop Loss Level:", min_value=0.0, format="%.2f")

# Output
if st.button("Calculate Option"):
    if market_spot > 0 and sl_level > 0 and target_level > 0:
        result = suggest_option(market_spot, target_level, sl_level, previous_trade, profit_or_loss)
        if "message" in result:
            st.markdown(result["message"], unsafe_allow_html=True)

        for key, value in result.items():
            if key != "message" and value != "":
                st.markdown(f"{key}: {value}", unsafe_allow_html=True)
    else:
        st.error("Please enter valid values for all fields.")
