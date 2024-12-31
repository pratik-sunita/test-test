import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from ta.momentum import RSIIndicator
from ta.trend import MACD


def fetch_stock_data(ticker, period='1y', interval='1d'):
    """
    Fetch historical stock data using yfinance.
    """
    print(f"Fetching data for {ticker}...")
    data = yf.download(ticker, period=period, interval=interval)
    if data.empty:
        print("Error: No data fetched. Please check the ticker symbol.")
        return None
    return data


def analyze_stock(data):
    """
    Analyze the stock data and provide recommendations based on technical indicators.
    """
    # Ensure 'Close' is a 1D pandas Series
    close_prices = data['Close'].squeeze()  # Flatten to 1D if needed

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

    # Print the last few rows for debugging (optional)
    print("\nLatest Data:")
    print(data.tail())

    # Ensure you access individual values correctly for condition checks
    last_row = data.iloc[-1]  # Get the last row of the DataFrame
    rsi_value = last_row['RSI']
    sma_50_value = last_row['SMA_50']
    sma_200_value = last_row['SMA_200']

    # Apply .item() to convert to scalar for comparison if necessary
    if isinstance(rsi_value, pd.Series):
        rsi_value = rsi_value.item()

    if isinstance(sma_50_value, pd.Series):
        sma_50_value = sma_50_value.item()

    if isinstance(sma_200_value, pd.Series):
        sma_200_value = sma_200_value.item()

    # Apply the condition logic now that values are scalars
    if rsi_value < 30 and sma_50_value < sma_200_value:
        return "Golden Opportunity: Buy and hold!"
    elif rsi_value > 70 or sma_50_value > sma_200_value:
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
    plt.show()


def main():
    """
    Main function to run the stock analysis.
    """
    ticker = input("Enter the stock ticker symbol: ").upper()
    data = fetch_stock_data(ticker)

    if data is not None:
        recommendation = analyze_stock(data)
        print("\nRecommendation:", recommendation)
        plot_data(data, ticker)


if __name__ == "__main__":
    main()
