import regex as re
import yfinance as yf
from textual import on
from textual_plot import PlotWidget, HiResMode
from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer, HorizontalGroup, VerticalGroup
from textual.widgets import Label, Header, Footer, Static, Button

### TEST DATA
# "TICKER": [QUANTITY, VALUE]
HOLDINGS = {
    "SAAB-B.ST": [1, 500],
    "SSAB-B.ST": [1, 500],
    "^OMX": [0, 0],
    "MSFT": [1, 500],
    "AAPL": [0, 0],
    "AMZN": [0,1]
}
LOCAL_CURRENCY = "SEK"

### SETTINGS ###
PERIOD = "1d" # timespan of data
INTERVAL = "1m" # granularity of data
UPDATE_INTERVAL = 600 ### How often to fetch prices, min 60=60 seconds

def Clean_symbol(symbol):
    return re.sub(r'[^a-zA-Z0-9]', '', str(symbol))

class StockManager:

    def __init__(self):
        self.stocks = {}

    def add_stock(self, stock):
        self.stocks[stock.symbol] = stock

    def __getitem__(self, key):
        return self.stocks[key]

def create_symbols():
    stocks = []  # Create new list
    for symbol in HOLDINGS.keys():
        quantity = HOLDINGS[symbol][0] # get quantity
        value = HOLDINGS[symbol][1] # get value
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
        return f'Stock({self.symbol!r}), Quant({self.quantity!r}), Price({self.value!r})'

class PortfolioOverview(Static):
    def __init__(self, stock_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stock_manager = stock_manager

    def convert_to_local_currency(self, symbol):
        stocklastclosed = self.stock_manager[symbol].close.iloc[-1]
        currencystring = LOCAL_CURRENCY + self.stock_manager[symbol].currency + "=X"
        currencyticker = yf.Ticker(currencystring)
        self.history = currencyticker.history()
        currencylastclosed = self.history['Close'].iloc[-1]
        value = stocklastclosed / currencylastclosed
        return value
        
    def compose(self) -> ComposeResult:
        """Widgets for Portfolio overview"""
        total = 0
        total_change = 0
        with HorizontalGroup(classes="allsymbols"):
            for symbol in HOLDINGS.keys():
                with VerticalGroup(classes="symbol"):
                    yield Label(f"{symbol}")
                    with HorizontalGroup(classes="symbolclosed"):
                        yield Label(f"Close: {self.stock_manager[symbol].close.iloc[-1]:.2f}")
                    with VerticalGroup(classes="symbolactual"):
                        actualvalue = self.stock_manager[symbol].close.iloc[-1] * HOLDINGS[symbol][0]
                        total += actualvalue
                        yield Label(f"Actual: {actualvalue:.2f}")
                    with VerticalGroup(classes="symbolchange"):
                        q = HOLDINGS[symbol][0]
                        v = HOLDINGS[symbol][1]
                        purchased_value = q * v
                        change = actualvalue - purchased_value
                        total_change += change
                        yield Label(f"{change:.2f}")
        yield Label(f"TOTAL WORTH: {total:.2f} ::: TOTAL CHANGE: {total_change:.2f}", classes="allsymbols")
    
        
    async def on_mount(self) -> None:
        self.set_interval(UPDATE_INTERVAL, self.refresh_price)

    async def refresh_price(self) -> None:
        for symbol in HOLDINGS.keys():
            label = self.query_one(f"#{Clean_symbol(symbol)}", expect_type=Label)
            price = self.stock_manager[symbol].close.iloc[-1]
            label.update(f"({price:.2f})")


class TickerPriceDisplay(Static):
    def __init__(self, symbol, stock_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stock_manager = stock_manager
        self.symbol = symbol  # Set symbol directly from argument

    async def on_mount(self) -> None:
        self.set_interval(UPDATE_INTERVAL, self.refresh_price)

    async def refresh_price(self) -> None:
            price = self.stock_manager[self.symbol].close.iloc[-1]
            self.update(f"{price:.2f}")

class SymbolTicker(Static):
    def __init__(self, symbol, stock_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.symbol = symbol
        self.stock_manager = stock_manager

    def compose(self) -> ComposeResult:
        """Widget for each symbol and graph"""
        with HorizontalGroup():
            yield Button(f"Remove Symbol {self.symbol}", id="remove")
            with VerticalGroup():
                yield TickerPriceDisplay(self.symbol, self.stock_manager, id=f"{Clean_symbol(self.symbol)}")
        yield PlotWidget(id="plot")

    def on_mount(self) -> None:
        plot = self.query_one(PlotWidget)
        symbol_data = self.stock_manager[self.symbol]
        plot.plot(x=symbol_data.datetime, y=symbol_data.close, hires_mode=HiResMode.BRAILLE)
        sticker = self.query_one(f"#{Clean_symbol(self.symbol)}")
        sticker.update(f"{self.stock_manager[self.symbol].close.iloc[-1]:.2f}")

    @on(Button.Pressed, "#remove")
    def remove_symbol(self) -> None:
        self.remove()


class SymbolWatcher(App):
    CSS_PATH = "style.css"
    BINDINGS = [
        ("a", "add_symbols", "Add symbols"),
        ("t", "toggle_dark", "Toggle dark mode")
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stock_manager = StockManager()
        symbols = create_symbols() 
        for symbol in symbols:
            self.stock_manager.add_stock(symbol)
    def compose(self) -> ComposeResult:
        """Widgets in this app"""
        yield Header(show_clock=True)
        yield PortfolioOverview(self.stock_manager)
        with ScrollableContainer(id="Symbols"):
            pass
        yield Footer()
        yield Footer()

    def action_toggle_dark(self):
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )
    def action_add_symbols(self):
        print("Creating Symbols with plots n stuff")
        for symbol in self.stock_manager.stocks:
            symbolticker = SymbolTicker(self.stock_manager[symbol].symbol, self.stock_manager)
            container = self.query_one("#Symbols")
            container.mount(symbolticker)
            symbolticker.scroll_visible()

if __name__ == "__main__":
    SymbolWatcher().run()