import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from ta.momentum import RSIIndicator
from ta.trend import MACD

# Function to fetch historical stock data
def fetch_stock_data(ticker, period='1y', interval='1d'):
    st.write(f"Fetching data for {ticker}...")
    data = yf.download(ticker, period=period, interval=interval)
    if data.empty:
        st.error("Error: No data fetched. Please check the ticker symbol.")
        return None
    return data

# Function to analyze the stock data
def analyze_stock(data):
    close_prices = data['Close'].squeeze()  # Flatten to 1D if needed

    data['SMA_50'] = close_prices.rolling(window=50).mean()
    data['SMA_200'] = close_prices.rolling(window=200).mean()

    rsi = RSIIndicator(close=close_prices)
    data['RSI'] = rsi.rsi()

    macd = MACD(close=close_prices)
    data['MACD'] = macd.macd()
    data['Signal_Line'] = macd.macd_signal()

    last_row = data.iloc[-1]
    rsi_value = round(last_row['RSI'], 2)
    sma_50_value = round(last_row['SMA_50'], 2)
    sma_200_value = round(last_row['SMA_200'], 2)
    macd_value = round(last_row['MACD'], 2)
    signal_line_value = round(last_row['Signal_Line'], 2)

    if isinstance(rsi_value, pd.Series):
        rsi_value = rsi_value.item()
    if isinstance(sma_50_value, pd.Series):
        sma_50_value = sma_50_value.item()
    if isinstance(sma_200_value, pd.Series):
        sma_200_value = sma_200_value.item()
    if isinstance(macd_value, pd.Series):
        macd_value = macd_value.item()
    if isinstance(signal_line_value, pd.Series):
        signal_line_value = signal_line_value.item()

    if rsi_value < 30 and sma_50_value < sma_200_value:
        recommendation = "Golden Opportunity: Buy and hold!"
        reason = (f"The RSI value is {rsi_value} (below 30), indicating the stock is oversold. "
                  f"Additionally, the 50-day SMA ({sma_50_value}) is below the 200-day SMA ({sma_200_value}), suggesting "
                  "a potential buying opportunity. This combination often signifies that the stock is undervalued and might "
                  "be poised for a rebound as investors recognize the discount price.")
    elif rsi_value > 70:
        recommendation = "Immediate Sale: Consider selling."
        reason = (f"The RSI value is {rsi_value} (above 70), indicating the stock is overbought. "
                  "This suggests a possible selling opportunity as the stock price may be inflated due to excessive buying, "
                  "leading to a potential price correction in the near term.")
    elif sma_50_value > sma_200_value:
        recommendation = "Immediate Sale: Consider selling."
        reason = (f"The 50-day SMA ({sma_50_value}) is above the 200-day SMA ({sma_200_value}), indicating a "
                  "possible selling opportunity. This crossover can signal that the stock price has been trending upward for "
                  "an extended period and might be due for a correction or consolidation phase.")
    else:
        recommendation = "Hold for now: Long-term potential."
        reason = (f"The RSI value is {rsi_value}, indicating neither an oversold nor overbought condition. "
                  f"The 50-day SMA ({sma_50_value}) is neither significantly above nor below the 200-day SMA ({sma_200_value}). "
                  "This suggests maintaining your current position could be prudent as there are no immediate signals of "
                  "extreme market conditions.")

    return recommendation, reason

# Function to plot the stock data
def plot_data(data, ticker):
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

# Streamlit app main function
def main():
    st.title("Stock Analysis App")
    st.write("Enter a stock ticker to analyze its technical indicators and get a recommendation.")

    ticker = st.text_input("Enter Stock Ticker (e.g., AAPL):").upper()
    if ticker:
        data = fetch_stock_data(ticker)
        if data is not None:
            recommendation, reason = analyze_stock(data)
            st.subheader("Recommendation")
            st.write(recommendation)
            st.subheader("**Why**")
            st.write(reason)
            plot_data(data, ticker)

    # Add disclaimer at the bottom
    st.markdown("""
    **Disclaimer:** The recommendations provided in this application are based on technical analysis using the Simple Moving Average (SMA), Relative Strength Index (RSI), and Moving Average Convergence Divergence (MACD) indicators. These suggestions are for informational purposes only and should not be considered as financial advice. The data and analyses presented are derived from historical stock prices and do not guarantee future performance. Users should conduct their own research and consult with a licensed financial advisor before making any investment decisions. The creator of this application is not responsible for any financial losses or gains incurred as a result of using this tool.
    """)

if __name__ == "__main__":
    main()
