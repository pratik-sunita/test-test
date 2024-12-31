import streamlit as st
import yfinance as yf

# Title of the app
st.title("Stock Data Analysis")

# Display a message that the app is fetching data
st.write("Fetching stock data...")

# Set the stock ticker symbol you want to analyze (you can change this)
ticker = "AAPL"  # Example: Apple stock (you can replace this with other ticker symbols)

# Fetch stock data using yfinance
try:
    # Download stock data for the last 5 years
    stock_data = yf.download(ticker, period="5y")

    # If data is fetched, display it
    if stock_data.empty:
        st.write(f"No data found for {ticker}")
    else:
        st.write(f"Data for {ticker}:")
        st.write(stock_data)

except Exception as e:
    # Show an error message if there's an issue with fetching data
    st.error(f"Error fetching data for {ticker}: {e}")
