import pandas as pd
import streamlit as st
import os
import ta
import mplfinance as mpf
import numpy as np
import datetime

st.title('Stock Analysis')
st.title("Do you want to use an indicator?")

choices = ["Yes", "No"]

# Radio button for user action
action = st.radio("Select an option:", choices, index=1)

# Display additional details only if "Yes" is selected
if action == "Yes":
    st.write("You selected 'Yes'. Here you can provide details or configure the indicators.")
    
    # Example of additional inputs when 'Yes' is selected
    indicator = st.selectbox("Choose an indicator:", ["Bollinger Bands", "RSI", "VWAP"])
    start_date = st.date_input("Start Date", datetime.date(2023, 1, 1))
    end_date = st.date_input("End Date", datetime.date(2024, 1, 1))
    
    st.write(f"Selected Indicator: {indicator}")
    st.write(f"Date Range: {start_date} to {end_date}")

elif action == "No":
    st.write("You selected 'No'. No further details to configure.")
