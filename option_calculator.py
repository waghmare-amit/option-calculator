import streamlit as st

# Apply custom CSS styling for underline (non-bold)
st.markdown("""
    <style>
    .underline {
        text-decoration: underline;
        font-weight: normal;
    }
    .warning-text {
        color: red;
        font-weight: bold;
        text-transform: uppercase;
    }
    .success-text {
        color: green;
        font-weight: bold;
        text-transform: uppercase;
    }
    </style>
""", unsafe_allow_html=True)

def suggest_option(market_spot, target_level, sl_level, prev_trade, pnl_value=None):
    delta_reference = {
        "Deep ITM": 0.8,
        "Slight ITM": 0.6,
        "ATM": 0.5,
        "Slight OTM": 0.4,
        "Deep OTM": 0.2
    }

    lot_size = 75
    max_loss = 1000
    max_profit = 3000
    delta = delta_reference["ATM"]
    actual_sl_points = abs(market_spot - sl_level)
    actual_target_points = abs(market_spot - target_level)
    best_strike = round(market_spot / 50) * 50
    suggested_type = "ATM"

    # Estimate ITM premium and adjust strike
    estimated_itm_premium = 1.2 * best_strike
    if estimated_itm_premium <= 12000:
        best_strike = best_strike - 50
        delta = delta_reference["Slight ITM"]
        suggested_type = "Slight ITM"

    sl_input_premium = round(actual_sl_points * delta, 2)
    target_input_premium = round(actual_target_points * delta, 2)

    if prev_trade == "No":
        sl_premium = round((max_loss / lot_size), 2)
        max_sl_points = round(sl_premium / delta, 2)
        max_sl_points = min(max_sl_points, 30)
        sl_premium_calc = round(max_sl_points * delta, 2)
        estimated_loss = round(sl_premium_calc * lot_size, 2)

        return {
            "<span class='underline'>The Best Strike to Buy</span>": best_strike,
            "Option Type": suggested_type,
            "Expected Delta": delta,
            "<span class='underline'>SL in Charts</span>": f"{actual_sl_points} (your input)",
            "<span class='underline'>Max SL Points</span>": f"{max_sl_points} (in charts, according to AI calculation for max loss of ₹{estimated_loss})",
            "<span class='underline'>SL in Premium</span>": f"{sl_premium_calc} (in broker, according to AI)",
            "<span class='underline'>SL in Premium Based on SL Input</span>": f"{sl_input_premium} (in broker, according to your input SL level)",
            "<span class='underline'>Target in Premium</span>": f"{target_input_premium} (in broker, according to your input target level)",
            "<span class='underline'>Estimated Loss</span>": f"₹{estimated_loss}"
        }

    if prev_trade == "Yes":
        if pnl_value < 0:
            new_max_loss = max_loss + pnl_value
            if new_max_loss <= 950:
                return "DONT TRADE, MAX LOSS FOR THE DAY IS DONE"
            max_loss_premium = new_max_loss / lot_size
            max_sl_points = round(max_loss_premium / delta, 2)
            max_sl_points = min(max_sl_points, 30)
            sl_premium_calc = round(max_sl_points * delta, 2)
            estimated_loss = round(sl_premium_calc * lot_size, 2)
            return {
                "<span class='underline'>The Best Strike to Buy</span>": best_strike,
                "Option Type": suggested_type,
                "Expected Delta": delta,
                "<span class='underline'>SL in Charts</span>": f"{actual_sl_points} (your input)",
                "<span class='underline'>Max SL Points</span>": f"{max_sl_points} (in charts, according to AI calculation for max loss of ₹{estimated_loss})",
                "<span class='underline'>SL in Premium</span>": f"{sl_premium_calc} (in broker, according to AI)",
                "<span class='underline'>SL in Premium Based on SL Input</span>": f"{sl_input_premium} (in broker, according to your input SL level)",
                "<span class='underline'>Target in Premium</span>": f"{target_input_premium} (in broker, according to your input target level)",
                "<span class='underline'>Estimated Loss</span>": f"₹{estimated_loss}"
            }

        elif pnl_value < max_profit:
            profit_left = max_profit - pnl_value
            trade_premium = round(profit_left / lot_size, 2)
            return {
                "<span class='underline'>The Best Strike to Buy</span>": best_strike,
                "Option Type": suggested_type,
                "Expected Delta": delta,
                "<span class='underline'>SL in Charts</span>": f"{actual_sl_points} (your input)",
                "<span class='underline'>Max SL Points</span>": f"{actual_sl_points} (in charts, according to AI calculation for max loss of ₹{round(sl_input_premium * lot_size, 2)})",
                "<span class='underline'>SL in Premium</span>": f"{sl_input_premium} (in broker, according to AI)",
                "<span class='underline'>SL in Premium Based on SL Input</span>": f"{sl_input_premium} (in broker, according to your input SL level)",
                "<span class='underline'>Target in Premium</span>": f"{target_input_premium} (in broker, according to your input target level)",
                "<span class='underline'>Trade in Premium According to Profit Earned</span>": f"{trade_premium} (in broker, based on earned profit)",
                "<span class='underline'>Estimated Loss</span>": f"₹{round(sl_input_premium * lot_size, 2)}"
            }

        elif pnl_value >= max_profit:
            return "YOU DON'T HAVE TO TRADE ANYMORE, SINCE MAX PROFIT HAS BEEN ACHIEVED"

# Streamlit UI
st.title("Option Strike Price Selector")

market_spot = st.number_input("Enter Market Spot Price:", min_value=0.0, format="%.2f")
prev_trade = st.radio("Any Previous Trades Made?", ("No", "Yes"))

pnl_value = None
if prev_trade == "Yes":
    pnl_value = st.number_input("Enter P/L Value of Previous Trade (Negative if Loss):", format="%.2f")

target_level = st.number_input("Enter Target Level:", min_value=0.0, format="%.2f")
sl_level = st.number_input("Enter Stop Loss Level:", min_value=0.0, format="%.2f")

if st.button("Calculate Option"):
    if market_spot > 0 and target_level > 0 and sl_level > 0:
        result = suggest_option(market_spot, target_level, sl_level, prev_trade, pnl_value)

        if isinstance(result, str):
            if "MAX LOSS" in result:
                st.markdown(f"<div class='warning-text'>{result}</div>", unsafe_allow_html=True)
            elif "MAX PROFIT" in result:
                st.markdown(f"<div class='success-text'>{result}</div>", unsafe_allow_html=True)
        else:
            st.markdown("### Suggested Option:")
            for key, value in result.items():
                st.markdown(f"{key}: {value}", unsafe_allow_html=True)
    else:
        st.error("Please enter all required values.")
