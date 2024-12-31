import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import matplotlib.pyplot as plt
import numpy as np


# Fetch stock data
def fetch_stock_data(ticker):
    data = yf.download(ticker, period="1y", interval="1d")
    if data.empty:
        st.error("No data found for this ticker symbol")
        return None
    return data


# Calculate technical indicators: RSI, SMA, MACD
def calculate_indicators(data):
    # Calculate RSI (Relative Strength Index)
    data['RSI'] = ta.momentum.RSIIndicator(data['Close']).rsi()

    # Calculate SMAs (Simple Moving Averages)
    data['SMA_50'] = data['Close'].rolling(window=50).mean()
    data['SMA_200'] = data['Close'].rolling(window=200).mean()

    # Calculate MACD (Moving Average Convergence Divergence)
    macd = ta.trend.MACD(data['Close'])
    data['MACD'] = macd.macd()
    data['MACD_signal'] = macd.macd_signal()

    return data


# Analyze the stock based on RSI, SMA, and MACD
def analyze_stock(data):
    # Take the last row of data for analysis
    last_row = data.iloc[-1]

    rsi_value = last_row['RSI']
    sma_50_value = last_row['SMA_50']
    sma_200_value = last_row['SMA_200']
    macd_value = last_row['MACD']
    macd_signal_value = last_row['MACD_signal']

    # Decision based on RSI, SMA, and MACD
    if rsi_value < 30 and sma_50_value < sma_200_value:
        return "Golden Opportunity: Buy and hold!"
    elif rsi_value > 70 or sma_50_value > sma_200_value or macd_value < macd_signal_value:
        return "Immediate Sale: Consider selling."
    else:
        return "Hold: No immediate action required."


# Plot the stock data with indicators
def plot_data(data, ticker):
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot closing price
    ax.plot(data['Close'], label='Close Price', color='blue')

    # Plot SMA lines
    ax.plot(data['SMA_50'], label='50-Day SMA', color='red', linestyle='--')
    ax.plot(data['SMA_200'], label='200-Day SMA', color='green', linestyle='--')

    ax.set_title(f'{ticker} Stock Price and Indicators')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price (USD)')
    ax.legend(loc='upper left')

    st.pyplot(fig)


# Streamlit App Layout
def main():
    st.title("Stock Analysis Tool")

    # Input: Ticker symbol
    ticker_input = st.text_input("Enter stock ticker (e.g., AAPL):")

    if ticker_input:
        data = fetch_stock_data(ticker_input)

        if data is not None:
            # Calculate indicators
            data = calculate_indicators(data)

            # Display analysis and recommendation
            recommendation = analyze_stock(data)
            st.subheader("Recommendation")
            st.write(recommendation)

            # Plot stock data and indicators
            plot_data(data, ticker_input)


if __name__ == "__main__":
    main()
