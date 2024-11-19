import streamlit as st
import datetime

st.title('Stock Analysis')
st.title("Do you want to use an indicator?")

choices = ["Yes", "No"]

# Radio button for user action with no initial selection
action = st.radio("Select an option:", choices, index=-1, key="indicator_choice")

# Show content based on the selected option
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
