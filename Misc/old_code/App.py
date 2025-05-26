import regex as re
import yfinance as yf
from textual import on
from textual_plot import PlotWidget
from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer, HorizontalGroup
from textual.widgets import Label, Header, Footer, Static, Button

### TEST DATA ###
SYMBOLS = ["SAAB", "MSFT", "AAPL", "AMZN", "IPCO"]
testdatax=[0, 1, 2, 3, 4]
testdatay=[0, 1, 4, 9, 16]
HOLDINGS = {
    "SAAB-B.ST": [1, 500],
    "SSAB-B.ST": [1, 500],
    "^OMX": [0, 0],
    "MSFT": [1, 500],
    "AAPL": [0, 0],
    "AMZN": [0,1]
}

### SETTINGS ###
PERIOD = "1d" # timespan of data
INTERVAL = "1m" # granularity of data
UPDATE_INTERVAL = 500 ### How often to fetch prices

class StockManager:

    def __init__(self):
        self.stocks = {}

    def add_stock(self, stock):
        self.stocks[stock.symbol] = stock

    def __getitem__(self, key):
        return self.stocks[key]

    def add_stock(self, stock):
        self.stocks[stock.symbol] = stock

def create_symbols():
    stocks = []  # Create new list
    for symbol in HOLDINGS.keys():
        quantity = HOLDINGS[symbol][0]
        value = HOLDINGS[symbol][1]
        stock = Symboldata(symbol, quantity, value)  # Assign instance to variable
        stocks.append(stock)   # Append that instance to list
    return stocks  # Return all newly created stocks

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

class PortfolioOverview(Static):
    def compose(self) -> ComposeResult:
        """Widgets for Portfolio overview"""
        with HorizontalGroup(id="symbolsgroup"):
            for id, symbol in enumerate(SYMBOLS):
                yield Label(f"{symbol}---", id=f"{symbol}")

class TickerPriceDisplay(Static):
    pass

class SymbolTicker(Static):
    def compose(self) -> ComposeResult:
        """Widget for each symbol and graph"""
        #yield Button("Plot", id="plot")
        yield Button("Remove Symbol", id="remove")
        yield TickerPriceDisplay("NaN: 0000:00")
        yield PlotWidget(id="plot")
###################################################################################
### FIGURE OUT A WAY TO GET DATA INTO A SPECIFIC SYMBOLTICKER ###
    def on_mount(self) -> None:
        stock_manager = StockManager()
        symbols = create_symbols() 
        for symbol in symbols:
            stock_manager.add_stock(symbol)
        plot = self.query_one(PlotWidget)
        plot.plot(x=testdatax, y= testdatay)

    @on(Button.Pressed, "#remove")
    def remove_symbol(self) -> None:
        self.remove()


class SymbolWatcher(App):
    CSS_PATH = "style.css"
    BINDINGS = [
        ("a", "add_symbol", "Add new symbol"),
        ("t", "toggle_dark", "Toggle dark mode")
    ]

    def compose(self) -> ComposeResult:
        """Widgets in this app"""
        yield Header()
        yield PortfolioOverview()
        with ScrollableContainer(id="Symbols"):
            pass
        yield Footer()

    def action_toggle_dark(self):
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )
    
    def action_add_symbol(self):
        stock_manager = StockManager()
        symbolticker = SymbolTicker()
        container = self.query_one("#Symbols")
        container.mount(symbolticker)
        symbolticker.scroll_visible()

if __name__ == "__main__":
    SymbolWatcher().run()