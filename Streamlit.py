import streamlit as st
import yfinance as yf
import pandas as pd
import ta

st.title("Stock Data Analysis")
st.write("Fetching stock data...")


# Function to fetch and analyze stock data
def analyze_stock(ticker):
    try:
        # Fetch historical stock data from Yahoo Finance (valid periods: 1mo, 3mo, 6mo, etc.)
        data = yf.download(ticker, period="3mo", interval="1d")

        # Check if the data is empty
        if data.empty:
            print(
                f"Could not fetch data for {ticker}. The data is empty. Please check the ticker symbol and try again.")
            return

        print(f"Data for {ticker} fetched successfully.")

        # Extract close prices and ensure it's 1D using .squeeze()
        close_prices = data['Close'].squeeze()  # This ensures the series is 1-dimensional

        # Calculate RSI (Relative Strength Index)
        rsi_indicator = ta.momentum.RSIIndicator(close=close_prices)
        rsi_series = rsi_indicator.rsi()

        # Calculate 50-period and 200-period SMAs (Simple Moving Averages)
        sma_50 = ta.trend.SMAIndicator(close=close_prices, window=50)
        sma_50_series = sma_50.sma_indicator()

        sma_200 = ta.trend.SMAIndicator(close=close_prices, window=200)
        sma_200_series = sma_200.sma_indicator()

        # Display the stock data
        print(f"Stock Data for {ticker}:")
        print(data.tail())

        # Extract the latest values for analysis
        latest_rsi = rsi_series.iloc[-1] if not rsi_series.empty else None
        latest_sma_50 = sma_50_series.iloc[-1] if not sma_50_series.empty else None
        latest_sma_200 = sma_200_series.iloc[-1] if not sma_200_series.empty else None

        # Example strategy (RSI < 30 is oversold, SMA_50 < SMA_200 is a bearish signal)
        if latest_rsi is not None and latest_sma_50 is not None and latest_sma_200 is not None:
            if latest_rsi < 30 and latest_sma_50 > latest_sma_200:
                print(f"{ticker} Recommendation: Buy! (Oversold and Bullish Signal)")
            elif latest_rsi > 70 and latest_sma_50 < latest_sma_200:
                print(f"{ticker} Recommendation: Sell! (Overbought and Bearish Signal)")
            else:
                print(f"{ticker} Recommendation: Hold (No clear signal)")
        else:
            print(f"Failed to calculate the technical indicators for {ticker}.")

    except Exception as e:
        print(f"Error fetching data for {ticker}: {str(e)}")


# Test with a ticker
ticker = "TSLA"
analyze_stock(ticker)
