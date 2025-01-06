import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from ta.trend import SMAIndicator
from ta.volume import VolumeWeightedAveragePrice
from textblob import TextBlob
import requests


@st.cache_data
def fetch_stock_data(ticker, period='1y', interval='1d'):
    """Fetch historical stock data using yfinance."""
    st.write(f"Fetching data for {ticker}...")
    data = yf.download(ticker, period=period, interval=interval)
    if data.empty:
        st.error("Error: No data fetched. Please check the ticker symbol.")
        return None
    return data


@st.cache_data
def fetch_news(ticker):
    """Fetch news articles related to the stock ticker."""
    api_key = 'f25ff0c2389e4546ad2bbc78becca545'
    url = f'https://newsapi.org/v2/everything?q={ticker}&apiKey={api_key}'
    response = requests.get(url)
    articles = response.json().get('articles', [])
    return articles


def analyze_sentiment(text):
    """Analyze sentiment of a given text."""
    analysis = TextBlob(text)
    return analysis.sentiment.polarity


def analyze_stock(data, avg_sentiment):
    """Analyze stock using technical indicators and provide recommendations."""
    # Ensure close prices are 1-dimensional
    close_prices = data['Close'].squeeze()

    # Bollinger Bands
    bollinger = BollingerBands(close=close_prices)
    data['BB_High'] = bollinger.bollinger_hband()
    data['BB_Low'] = bollinger.bollinger_lband()

    # RSI Indicator
    rsi = RSIIndicator(close=close_prices)
    data['RSI'] = rsi.rsi()

    # 50-day and 200-day Simple Moving Average (SMA)
    sma_50 = SMAIndicator(close=close_prices, window=50)
    data['SMA_50'] = sma_50.sma_indicator()

    sma_200 = SMAIndicator(close=close_prices, window=200)
    data['SMA_200'] = sma_200.sma_indicator()

    # Volume Weighted Average Price (VWAP)
    vwap = VolumeWeightedAveragePrice(
        high=data['High'].squeeze(),
        low=data['Low'].squeeze(),
        close=data['Close'].squeeze(),
        volume=data['Volume'].squeeze()
    )
    data['VWAP'] = vwap.volume_weighted_average_price()

    # Get the last row of data
    last_row = data.iloc[-1]

    # Extract scalar values with .item() if applicable
    rsi_value = last_row['RSI'] if pd.notnull(last_row['RSI']).any() else None
    bb_high_value = last_row['BB_High'] if pd.notnull(last_row['BB_High']).any() else None
    bb_low_value = last_row['BB_Low'] if pd.notnull(last_row['BB_Low']).any() else None
    close_value = last_row['Close'] if pd.notnull(last_row['Close']).any() else None

    if isinstance(rsi_value, pd.Series):
        rsi_value = rsi_value.iloc[0]
    if isinstance(bb_high_value, pd.Series):
        bb_high_value = bb_high_value.iloc[0]
    if isinstance(bb_low_value, pd.Series):
        bb_low_value = bb_low_value.iloc[0]
    if isinstance(close_value, pd.Series):
        close_value = close_value.iloc[0]

    # Recommendation logic based on sentiment and indicators
    if avg_sentiment < 0:  # Negative market sentiment
        recommendation = "Consider Selling: Negative sentiment in the market."
        reason = f"Market sentiment polarity is {avg_sentiment:.2f}."
    elif rsi_value is not None and bb_low_value is not None and close_value is not None and rsi_value < 20 and close_value <= bb_low_value:
        recommendation = "Golden Opportunity: Buy and hold!"
        reason = f"RSI is {rsi_value} (oversold) and price is near lower Bollinger Band ({bb_low_value})."
    elif rsi_value is not None and bb_high_value is not None and close_value is not None and rsi_value > 80 and close_value >= bb_high_value:
        recommendation = "Immediate Sale: Consider selling."
        reason = f"RSI is {rsi_value} (overbought) and price is near upper Bollinger Band ({bb_high_value})."
    elif rsi_value is not None and rsi_value < 30:
        recommendation = "Consider Buying: RSI suggests oversold."
        reason = f"RSI is {rsi_value} (oversold)."
    elif rsi_value is not None and rsi_value > 70:
        recommendation = "Consider Selling: RSI suggests overbought."
        reason = f"RSI is {rsi_value} (overbought)."
    elif close_value is not None and close_value <= bb_low_value:
        recommendation = "Consider Buying: Price near lower Bollinger Band."
        reason = f"Price is near lower Bollinger Band ({bb_low_value})."
    elif close_value is not None and close_value >= bb_high_value:
        recommendation = "Consider Selling: Price near upper Bollinger Band."
        reason = f"Price is near upper Bollinger Band ({bb_high_value})."
    else:
        recommendation = "Hold for now: Monitoring situation."
        reason = "Indicators do not show strong buy or sell signals."

    return recommendation, reason


def plot_data(data, ticker):
    """Plot stock data using Matplotlib."""
    plt.figure(figsize=(14, 7))
    plt.plot(data['Close'], label='Close Price', color='blue')
    plt.plot(data['SMA_50'], label='50-Day SMA', color='green')
    plt.plot(data['SMA_200'], label='200-Day SMA', color='red')
    plt.plot(data['BB_High'], label='Bollinger Band High', color='magenta')
    plt.plot(data['BB_Low'], label='Bollinger Band Low', color='cyan')
    plt.plot(data['VWAP'], label='VWAP', color='orange')
    plt.title(f"{ticker} Stock Analysis")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.grid()
    st.pyplot(plt)


def main():
    """Streamlit app main function."""
    st.title("Stock Analysis App")
    st.write("Enter a stock ticker to analyze its technical indicators and get a recommendation.")

    ticker = st.text_input("Enter Stock Ticker (e.g., AAPL):").upper()
    if ticker:
        data = fetch_stock_data(ticker)
        if data is not None:
            news_articles = fetch_news(ticker)
            sentiments = [
                analyze_sentiment((article.get('title') or '') + '. ' + (article.get('description') or ''))
                for article in news_articles
            ]
            avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0

            recommendation, reason = analyze_stock(data, avg_sentiment)
            st.subheader("Recommendation")
            st.write(recommendation)
            st.subheader("**Why**")
            st.write(reason)

            if avg_sentiment != 0:
                st.subheader("**Market Sentiment**")
                st.write(f"Average Sentiment Polarity: {avg_sentiment:.2f}")

            plot_data(data, ticker)

            st.markdown("""**Disclaimer:** This app provides analysis based on technical and sentiment indicators. It is not financial advice.""")

if __name__ == "__main__":
    main()
