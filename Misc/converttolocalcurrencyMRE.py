import yfinance as yf
import time

LOCAL_CURRENCY = "SEK"

class CurrencyConvert:
    def __init__(self):
        self.currency_cache = {}  # {currencystring: (timestamp, last_close)}
        self.stock_manager = {}

    def convert_to_local_currency(self, symbol):
        """
        Convert the last closing price of a symbol to the local currency.
        Fetches the latest exchange rate using Yahoo Finance and converts the
        stock's closing price to the local currency.
        Args:
            symbol (str): The symbol to convert.
        Returns:
            float: The converted price in local currency.
        """
        stocklastclosed = self.stock_manager[symbol].close.iloc[-1]  # Last close price
        currencystring = LOCAL_CURRENCY + self.stock_manager[symbol].currency + "=X"  # Currency pair string

        now = time.time()
        cache = self.currency_cache.get(currencystring)
        if cache is None or now - cache[0] > 60:
            currencyticker = yf.Ticker(currencystring)
            history = currencyticker.history()
            currencylastclosed = history['Close'].iloc[-1]
            self.currency_cache[currencystring] = (now, currencylastclosed)
        else:
            currencylastclosed = cache[1]

        value = stocklastclosed / currencylastclosed  # Convert to local currency
        return value
    
