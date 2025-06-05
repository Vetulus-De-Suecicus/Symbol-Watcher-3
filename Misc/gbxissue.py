import yfinance as yf

stock = yf.Ticker("BA.L")  # Fetch ticker data
history = stock.history(   # Get historical data
                        period="1d",
                        interval="1m"
                        )
datetime = history.index  # Get datetime index
datetime = list(range(len(datetime)))  # Convert to list
close = history["Close"]  # Closing prices
open = history["Open"]  # Opening prices
high = history["High"]  # High prices
low = history["Low"]  # Low prices
volume = history["Volume"]  # Volume data
currency = stock.info["currency"]  # Currency of the stock

print(currency)