import yfinance as yf
import regex as re

PERIOD = "1d" # timespan of data
INTERVAL = "1m" # granularity of data

HOLDINGS = {
    "SAAB-B.ST": [1, 500],
    "SSAB-B.ST": [1, 500],
    "^OMX": [0, 0],
    "MSFT": [1, 500],
    "AAPL": [0, 0],
    "AMZN": [0,1]
}

def Clean_symbol(symbol):
    return re.sub(r'[^a-zA-Z0-9]', '', str(symbol))

def create_symbols():
    stocks = []  # Create new list
    for symbol in HOLDINGS.keys():
        quantity = HOLDINGS[symbol][0]
        value = HOLDINGS[symbol][1]
        stock = Symboldata(symbol, quantity, value)  # Assign instance to variable
        stocks.append(stock)   # Append that instance to list
    return stocks  # Return all newly created stocks

# def create_symbols():
#     for symbol in HOLDINGS.keys():
#         quantity = HOLDINGS[symbol][0]
#         value = HOLDINGS[symbol][1]
#         Symboldata(symbol, quantity, value)

class Symboldata():
    """Fetches financial data from yahoo"""
    def __init__(self,symbol, quantity, value):
        self.symbol = symbol
        self.quantity = quantity
        self.value = value
        stock = yf.Ticker(self.symbol)
        self.history = stock.history(period=PERIOD, interval=INTERVAL)
        self.datetime = self.history.index
        self.datetime = list(range(len(self.datetime)))
        self.close = self.history["Close"]
        self.open = self.history["Open"]
        self.high = self.history["High"]
        self.low = self.history["Low"]
        self.volume = self.history["Volume"]
        self.currency = stock.info["currency"]

    def __repr__(self):
        return f'Stock({self.symbol!r}), Quant({self.quantity}), Price({self.value})'

class StockManager:

    def __init__(self):
        self.stocks = {}

    def add_stock(self, stock):
        self.stocks[stock.symbol] = stock

    def __getitem__(self, key):
        return self.stocks[key]

    def add_stock(self, stock):
        self.stocks[stock.symbol] = stock

stock_manager = StockManager()
symbols = create_symbols() 
for symbol in symbols:
    stock_manager.add_stock(symbol)

print(stock_manager.stocks)

for symbol, (quantity, value) in HOLDINGS.items():
    if not stock_manager[symbol].history.empty:
        closing = stock_manager[symbol].close.iloc[-1]
        print(closing)
