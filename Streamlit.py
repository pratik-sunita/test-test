import yfinance as yf
import pandas as pd
import streamlit as st
from ta.momentum import RSIIndicator
from ta.trend import MACD
import matplotlib.pyplot as plt

def fetch_stock_data(ticker, period='1y', interval='1d'):
    """
    Fetch historical stock data using yfinance.
    """
    st.write(f"Fetching data for {ticker}...")
    data = yf.download(ticker, period=period, interval=interval)
    if data.empty:
        st.error("Error: No data fetched. Please check the ticker symbol.")
        return None
    return data

def analyze_stock(data):
    """
    Analyze the stock data and provide recommendations based on technical indicators.
    """
    close_prices = data['Close'].squeeze()

    # Calculate Moving Averages
    data['SMA_50'] = close_prices.rolling(window=50).mean()
    data['SMA_200'] = close_prices.rolling(window=200).mean()

    # Calculate RSI
    rsi = RSIIndicator(close=close_prices)
    data['RSI'] = rsi.rsi()

    # Calculate MACD
    macd = MACD(close=close_prices)
    data['MACD'] = macd.macd()
    data['Signal_Line'] = macd.macd_signal()

    # Recommendation logic based on technical indicators
    last_row = data.iloc[-1]
    rsi_value = last_row['RSI']
    sma_50_value = last_row['SMA_50']
    sma_200_value = last_row['SMA_200']

    # Decision based on RSI, SMA, and MACD
    if (rsi_value < 30) & (sma_50_value < sma_200_value):
        return "Golden Opportunity: Buy and hold!"
    elif (rsi_value > 70) | (sma_50_value > sma_200_value):
        return "Immediate Sale: Consider selling."
    else:
        return "Hold for now: Long-term potential."

def plot_data(data, ticker):
    """
    Plot the stock data with indicators.
    """
    plt.figure(figsize=(14, 7))
    plt.plot(data['Close'], label='Close Price', color='blue')
    plt.plot(data['SMA_50'], label='50-Day SMA', color='green')
    plt.plot(data['SMA_200'], label='200-Day SMA', color='red')
    plt.title(f"{ticker} Stock Analysis")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.grid()
    st.pyplot(plt)

# Streamlit UI
st.title("Stock Data Analysis")
ticker_input = st.text_input("Enter Stock Ticker Symbol:", value="AAPL")

if ticker_input:
    data = fetch_stock_data(ticker_input)

    if data is not None:
        recommendation = analyze_stock(data)
        st.subheader("Recommendation")
        st.write(recommendation)
        plot_data(data, ticker_input)
