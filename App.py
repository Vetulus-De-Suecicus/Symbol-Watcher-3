# Import necessary libraries
import regex as re  # For regular expressions
import yfinance as yf  # For fetching financial data
from textual import on  # For event handling in textual
from textual_plot import PlotWidget, HiResMode  # For plotting widgets
from textual.app import App, ComposeResult  # Main app and composition
from textual.containers import ScrollableContainer, HorizontalGroup, VerticalGroup, Container  # Layout containers
from textual.widgets import Label, Header, Footer, Static, Button, Digits  # UI widgets

### TEST DATA
# Dictionary of holdings: "TICKER": [QUANTITY, VALUE IN LOCAL CURRENCY]
HOLDINGS = {
    "SAAB-B.ST": [1, 500],
    "SSAB-B.ST": [1, 500],
    "^OMX": [0, 0],
    "MSFT": [1, 500],
    "AAPL": [0, 0],
    "AMZN": [0,1]
}
LOCAL_CURRENCY = "SEK"  # Local currency for conversion

### SETTINGS ###
PERIOD = "1d"  # Timespan of data to fetch
INTERVAL = "1m"  # Data granularity
UPDATE_INTERVAL = 60  # How often to fetch prices (in seconds), min 60

def Clean_symbol(symbol):
    """Remove all non-alphanumeric characters from symbol string."""
    return re.sub(r'[^a-zA-Z0-9]', '', str(symbol))

class StockManager:
    """Manages a collection of stock data objects."""

    def __init__(self):
        self.stocks = {}  # Dictionary to hold stock objects

    def add_stock(self, stock):
        """Add a stock object to the manager."""
        self.stocks[stock.symbol] = stock

    def __getitem__(self, key):
        """Allow dictionary-like access to stocks."""
        return self.stocks[key]

def create_symbols():
    """Create Symboldata objects for each holding and return as a list."""
    stocks = []
    for symbol in HOLDINGS.keys():
        quantity = HOLDINGS[symbol][0]  # Get quantity
        value = HOLDINGS[symbol][1]  # Get value
        stock = Symboldata(symbol, quantity, value)  # Create Symboldata instance
        stocks.append(stock)  # Add to list
    return stocks

class Symboldata():
    """Fetches and stores financial data for a symbol from Yahoo Finance."""
    def __init__(self,symbol, quantity, value):
        self.symbol = symbol
        self.quantity = quantity
        self.value = value
        stock = yf.Ticker(self.symbol)  # Fetch ticker data
        self.history = stock.history(period=PERIOD, interval=INTERVAL)  # Get historical data
        self.datetime = self.history.index  # Get datetime index
        self.datetime = list(range(len(self.datetime)))  # Convert to list of indices for plotting
        self.close = self.history["Close"]  # Closing prices
        self.open = self.history["Open"]  # Opening prices
        self.high = self.history["High"]  # High prices
        self.low = self.history["Low"]  # Low prices
        self.volume = self.history["Volume"]  # Volume data
        self.currency = stock.info["currency"]  # Currency of the stock
        
    def __repr__(self):
        """String representation for debugging."""
        return f'Stock({self.symbol!r}), Quant({self.quantity!r}), Price({self.value!r})'

class PortfolioOverview(Container):
    """Widget to display an overview of the portfolio."""

    def __init__(self, stock_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stock_manager = stock_manager  # Reference to StockManager

    def convert_to_local_currency(self, symbol):
        """Convert the last closing price of a symbol to local currency."""
        stocklastclosed = self.stock_manager[symbol].close.iloc[-1]  # Last close price
        currencystring = LOCAL_CURRENCY + self.stock_manager[symbol].currency + "=X"  # Currency pair string
        currencyticker = yf.Ticker(currencystring)  # Fetch currency data
        self.history = currencyticker.history()  # Get currency history
        currencylastclosed = self.history['Close'].iloc[-1]  # Last close price of currency
        value = stocklastclosed / currencylastclosed  # Convert to local currency
        return value
        
    def compose(self) -> ComposeResult:
        """Compose widgets for portfolio overview."""
        total = 0  # Total portfolio value
        total_change = 0  # Total change in value
        with HorizontalGroup(classes="allsymbols"):
            for symbol in HOLDINGS.keys():
                with VerticalGroup(classes="symbol"):
                    yield Label(f"{symbol}")  # Symbol label
                    with HorizontalGroup(classes="symbolclosed"):
                        # Show close price, convert if needed
                        if self.stock_manager[symbol].currency == LOCAL_CURRENCY:
                            yield Label(f"Close: {self.stock_manager[symbol].close.iloc[-1]:.2f}:{self.stock_manager[symbol].currency}", id=f"{Clean_symbol(symbol)}")
                        else:
                            convertedlaststock = self.convert_to_local_currency(symbol)
                            yield Label(f"CloseCV: {convertedlaststock:.2f}:{LOCAL_CURRENCY}", id=f"{Clean_symbol(symbol)}")
                    with VerticalGroup(classes="symbolactual"):
                        # Calculate actual value (converted if needed)
                        if self.stock_manager[symbol].currency == LOCAL_CURRENCY:
                            actualvalue = self.stock_manager[symbol].close.iloc[-1] * self.stock_manager[symbol].quantity
                            total += actualvalue
                        else:
                            actualvalue = self.convert_to_local_currency(symbol) * self.stock_manager[symbol].quantity
                            total += actualvalue
                        yield Label(f"Actual: {actualvalue:.2f}", id=f"{Clean_symbol(symbol)}actual")
                    with VerticalGroup(classes="symbolchange"):
                        # Calculate change from purchase value
                        purchased_value = self.stock_manager[symbol].quantity * self.stock_manager[symbol].value
                        change = actualvalue - purchased_value
                        total_change += change
                        yield Label(f"Changed: {change:.2f}", id=f"{Clean_symbol(symbol)}change")
        # Show totals
        yield Label(f"TOTAL WORTH: {total:.2f}:{LOCAL_CURRENCY} ::: TOTAL CHANGE: {total_change:.2f}:{LOCAL_CURRENCY}", id=f"{Clean_symbol(symbol)}total", classes="allsymbols")
    
    async def on_mount(self) -> None:
        """Set up periodic price refresh on mount."""
        self.set_interval(UPDATE_INTERVAL, self.refresh_price)

    async def refresh_price(self) -> None:
        """Refresh prices for all symbols."""
        for symbol in HOLDINGS.keys():
            closing = self.query_one(f"#{Clean_symbol(symbol)}", expect_type=Label)
            actual = self.query_one(f"#{Clean_symbol(symbol)}actual", expect_type=Label)
            change = self.query_one(f"#{Clean_symbol(symbol)}change", expect_type=Label)
            
            if self.stock_manager[symbol].currency == LOCAL_CURRENCY:
                # Closing updated prices
                closingprice = self.stock_manager[symbol].close.iloc[-1]
                currencyclosing = self.stock_manager[symbol].currency
                closing.update(f"Close: {closingprice:.2f}:{currencyclosing}")
                
                # Actual updated prices
                actualvalue = self.stock_manager[symbol].close.iloc[-1] * self.stock_manager[symbol].quantity
                actual.update(f"Actual: {actualvalue:.2f}")

                # Changed prices updated
                purchased_value = self.stock_manager[symbol].quantity * self.stock_manager[symbol].value
                changedvalue = actualvalue - purchased_value
                change.update(f"Changed: {changedvalue:.2f}")
            elif self.stock_manager[symbol].currency != LOCAL_CURRENCY:
                # Closing updated prices for converted currency
                convertedlaststock = self.convert_to_local_currency(symbol)
                closing.update(f"Close: {convertedlaststock:.2f}:{LOCAL_CURRENCY}")

                # Actual updated prices for converted currency
                actualvalue = self.convert_to_local_currency(symbol) * self.stock_manager[symbol].quantity
                actual.update(f"Actual: {actualvalue:.2f}")

                # Changed prices updated for converted currency
                purchased_value = self.stock_manager[symbol].quantity * self.stock_manager[symbol].value
                changedvalue = actualvalue - purchased_value
                change.update(f"Changed: {changedvalue:.2f}")

class TickerPriceDisplay(Digits):
    """Widget to display the current price of a ticker."""

    def __init__(self, symbol, stock_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stock_manager = stock_manager  # Reference to StockManager
        self.symbol = symbol  # Symbol to display

    async def on_mount(self) -> None:
        """Set up periodic price refresh on mount."""
        self.set_interval(UPDATE_INTERVAL, self.refresh_price)

    async def refresh_price(self) -> None:
        """Refresh the displayed price."""
        price = self.stock_manager[self.symbol].close.iloc[-1]
        self.update(f"{price:.2f}")

class SymbolTicker(Static):
    """Widget for a symbol, including price and plot."""

    def __init__(self, symbol, stock_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.symbol = symbol  # Symbol to display
        self.stock_manager = stock_manager  # Reference to StockManager

    def compose(self) -> ComposeResult:
        """Compose widgets for the symbol ticker."""
        with HorizontalGroup():
            yield Button(f"Remove Symbol {self.symbol}", id="remove")  # Remove button
            yield TickerPriceDisplay(self.symbol, self.stock_manager, id=f"{Clean_symbol(self.symbol)}")  # Price display
        yield PlotWidget(id="plot")  # Plot widget

    def on_mount(self) -> None:
        """Plot the symbol's data and update price on mount."""
        plot = self.query_one(PlotWidget)
        symbol_data = self.stock_manager[self.symbol]
        plot.plot(x=symbol_data.datetime, y=symbol_data.close, hires_mode=HiResMode.BRAILLE)
        sticker = self.query_one(f"#{Clean_symbol(self.symbol)}")
        sticker.update(f"{self.stock_manager[self.symbol].close.iloc[-1]:.2f}")

    @on(Button.Pressed, "#remove")
    def remove_symbol(self) -> None:
        """Remove this symbol widget when the button is pressed."""
        self.remove()

class SymbolWatcher(App):
    """Main application class for the Symbol Watcher."""

    CSS_PATH = "style.css"  # Path to CSS file
    BINDINGS = [
        ("a", "add_symbols", "Add symbols"),
        ("s", "toggle_overview", "Toggle Overview")
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stock_manager = StockManager()  # Create stock manager
        symbols = create_symbols()  # Create symbol data objects
        for symbol in symbols:
            self.stock_manager.add_stock(symbol)  # Add to manager

    def compose(self) -> ComposeResult:
        """Compose the main app widgets."""
        yield Header(show_clock=True)  # Header with clock
        yield PortfolioOverview(self.stock_manager, classes="-hidden")  # Portfolio overview
        with ScrollableContainer(id="Symbols"):
            pass  # Container for symbol tickers
        yield Footer()  # Footer
        yield Footer()  # (Possibly redundant) second footer
    
    def on_mount(self):
        self.theme = "nord"

    def action_toggle_overview(self) -> None:
        self.query_one(PortfolioOverview).toggle_class("-hidden")

    def action_add_symbols(self):
        """Add symbol tickers to the UI."""
        print("Creating Symbols with plots n stuff")
        for symbol in self.stock_manager.stocks:
            symbolticker = SymbolTicker(self.stock_manager[symbol].symbol, self.stock_manager)
            container = self.query_one("#Symbols")
            container.mount(symbolticker)
            symbolticker.scroll_visible()

if __name__ == "__main__":
    SymbolWatcher().run()  # Run the app