# Import necessary libraries
import time
import json
import regex as re  # For regular expressions
import yfinance as yf  # For fetching financial data
from textual import on  # For event handling in textual
from textual.screen import ModalScreen 
from textual.app import App, ComposeResult  # Main app and composition
from textual_plot import PlotWidget, HiResMode  # For plotting widgets
from textual.widgets import Label, Header, Footer, Static, Button, Digits  # UI widgets
from textual.containers import ScrollableContainer, HorizontalGroup, VerticalGroup, Container  # Layout containers


# For dictionary of holdings: "TICKER": [QUANTITY, VALUE IN LOCAL CURRENCY]
def load_holdings(filename="holdings.json"):
    """
    Load holdings data from a JSON file.

    Attempts to open and parse the specified JSON file containing the user's stock holdings.
    Each holding should be structured as "TICKER": [QUANTITY, VALUE IN LOCAL CURRENCY].
    If the file does not exist, returns an empty dictionary.

    Args:
        filename (str): The path to the JSON file containing holdings data.

    Returns:
        dict: A dictionary mapping ticker symbols to their quantity and value.
    """
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def load_settings(filename="settings.json"):
    """
    Load application settings from a JSON file.

    Reads the specified JSON file to load user-configurable settings such as PERIOD, INTERVAL, and UPDATE_INTERVAL.
    These settings control the timespan of data to fetch, the data granularity, and how often prices are updated.
    If the file does not exist, returns an empty dictionary.

    Args:
        filename (str): The path to the JSON file containing application settings.

    Returns:
        dict: A dictionary containing settings for PERIOD, INTERVAL, LOCAL_CURRENCY, and UPDATE_INTERVAL.
    """
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def Clean_symbol(symbol):
    """
    Sanitize a symbol string by removing all non-alphanumeric characters.

    This function ensures that the symbol string is safe for use as an identifier
    in UI elements or queries by stripping out any characters that are not letters or numbers.

    Args:
        symbol (str): The symbol string to clean.

    Returns:
        str: The cleaned symbol string containing only alphanumeric characters.
    """
    return re.sub(r'[^a-zA-Z0-9]', '', str(symbol))

class StockManager:
    """
    Manages a collection of Symboldata objects representing stock holdings.

    Provides methods to add new stock data and access them in a dictionary-like manner.
    Used as a central repository for all stock-related data within the application.
    """

    def __init__(self):
        self.stocks = {}  # Dictionary to hold stock objects

    def add_stock(self, stock):
        """
        Add a Symboldata object to the manager.

        Args:
            stock (Symboldata): The stock data object to add.
        """
        self.stocks[stock.symbol] = stock

    def __getitem__(self, key):
        """
        Retrieve a Symboldata object by its symbol.

        Args:
            key (str): The symbol of the stock to retrieve.

        Returns:
            Symboldata: The corresponding stock data object.
        """
        return self.stocks[key]

class CurrencyConvert:
    def __init__(self, stock_manager):
        self.currency_cache = {}  # {currencystring: (timestamp, last_close)}
        self.stock_manager = stock_manager

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

def create_symbols():
    """
    Create Symboldata objects for each holding in the user's portfolio.

    Iterates through the loaded holdings and instantiates a Symboldata object for each,
    using the symbol, quantity, and purchase value. Returns a list of these objects.

    Returns:
        list: A list of Symboldata instances for each holding.
    """
    stocks = []
    for symbol in HOLDINGS.keys():
        quantity = HOLDINGS[symbol][0]  # Get quantity
        value = HOLDINGS[symbol][1]  # Get value
        stock = Symboldata(symbol, quantity, value)  # Create Symboldata instance
        stocks.append(stock)  # Add to list
    return stocks

class HelpScreen(ModalScreen):
    """
    Modal screen displaying help and usage instructions.

    Informs the user about configuration requirements and value presentation.
    Can be dismissed with the Escape key.
    """
    BINDINGS = [("escape", "dismiss")]

    def compose(self) -> ComposeResult:
        with Container(id="help-screen-container"):
            yield Label("Remember to set LOCAL_CURRENCY and HOLDINGS correctly")
            yield Label(f"All values are presented in {LOCAL_CURRENCY} for the Overview")
            yield Label(f"All values are NOT presented in {LOCAL_CURRENCY} for the Plots/Graphs")
            yield Label("Press ESC to exit")

class Symboldata():
    """
    Represents and fetches financial data for a single stock symbol.

    On initialization, retrieves historical price and volume data from Yahoo Finance,
    stores relevant information such as open, close, high, low, and volume, and
    determines the currency of the stock. Used as the data model for each holding.

    Attributes:
        symbol (str): The stock symbol.
        quantity (float): Number of shares held.
        value (float): Purchase value per share in local currency.
        history (DataFrame): Historical price data.
        datetime (list): List of indices for plotting.
        close (Series): Closing prices.
        open (Series): Opening prices.
        high (Series): High prices.
        low (Series): Low prices.
        volume (Series): Volume data.
        currency (str): Currency of the stock.
    """
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
        """
        Return a string representation of the Symboldata object for debugging.

        Returns:
            str: Debug string with symbol, quantity, and price.
        """
        return f'Stock({self.symbol!r}), Quant({self.quantity!r}), Price({self.value!r})'

class PortfolioOverview(Container):
    """
    Widget that displays an overview of the user's entire portfolio.

    Shows each holding's symbol, current price (converted to local currency if needed),
    actual value, and change from purchase value. Also displays total portfolio worth
    and total change. Periodically refreshes prices and updates the display.

    Args:
        stock_manager (StockManager): The manager containing all Symboldata objects.
    """
    def __init__(self, stock_manager, currency_convert, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stock_manager = stock_manager  # Reference to StockManager
        self.currency_convert = currency_convert
        
    def compose(self) -> ComposeResult:
        """
        Compose the widgets for the portfolio overview display.

        Iterates through all holdings, displaying symbol, price, actual value,
        and change for each. Also shows total worth and total change.

        Returns:
            ComposeResult: The composed UI elements.
        """
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
                            convertedlaststock = self.currency_convert.convert_to_local_currency(symbol)
                            yield Label(f"Close: {convertedlaststock:.2f}:{LOCAL_CURRENCY}", id=f"{Clean_symbol(symbol)}")
                    with VerticalGroup(classes="symbolactual"):
                        # Calculate actual value (converted if needed)
                        if self.stock_manager[symbol].currency == LOCAL_CURRENCY:
                            actualvalue = self.stock_manager[symbol].close.iloc[-1] * self.stock_manager[symbol].quantity
                            total += actualvalue
                        else:
                            actualvalue = self.currency_convert.convert_to_local_currency(symbol) * self.stock_manager[symbol].quantity
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
        """
        Set up periodic price refresh when the widget is mounted.

        Starts a timer to refresh prices at the interval specified by UPDATE_INTERVAL.
        """
        self.set_interval(UPDATE_INTERVAL, self.refresh_price)

    async def refresh_price(self) -> None:
        """
        Refresh the displayed prices, actual values, and changes for all holdings.

        Updates the UI elements for each symbol with the latest data, converting
        to local currency if necessary.
        """
        create_symbols()
        for symbol in HOLDINGS.keys():
            closing = self.query_one(f"#{Clean_symbol(symbol)}", expect_type=Label)
            actual = self.query_one(f"#{Clean_symbol(symbol)}actual", expect_type=Label)
            change = self.query_one(f"#{Clean_symbol(symbol)}change", expect_type=Label)
            closing.loading = True
            change.loading = True
            actual.loading = True
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
                convertedlaststock = self.currency_convert.convert_to_local_currency(symbol)
                closing.update(f"Close: {convertedlaststock:.2f}:{LOCAL_CURRENCY}")

                # Actual updated prices for converted currency
                actualvalue = self.currency_convert.convert_to_local_currency(symbol) * self.stock_manager[symbol].quantity
                actual.update(f"Actual: {actualvalue:.2f}")

                # Changed prices updated for converted currency
                purchased_value = self.stock_manager[symbol].quantity * self.stock_manager[symbol].value
                changedvalue = actualvalue - purchased_value
                change.update(f"Changed: {changedvalue:.2f}")

            closing.loading = False
            change.loading = False
            actual.loading = False
            
class TickerPriceDisplay(Digits):
    """
    Widget for displaying the current price of a specific ticker symbol.

    Periodically updates to show the latest price for the given symbol.
    Used within SymbolTicker widgets to provide real-time price feedback.

    Args:
        symbol (str): The symbol to display.
        stock_manager (StockManager): Reference to the stock manager.
    """

    def __init__(self, symbol, stock_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stock_manager = stock_manager  # Reference to StockManager
        self.symbol = symbol  # Symbol to display

    async def on_mount(self) -> None:
        """
        Set up periodic price refresh when the widget is mounted.

        Starts a timer to refresh the displayed price at the interval specified by UPDATE_INTERVAL.
        """
        self.set_interval(UPDATE_INTERVAL, self.refresh_price)

    async def refresh_price(self) -> None:
        """
        Refresh the displayed price for the ticker symbol.

        Updates the widget with the latest closing price.
        """
        price = self.stock_manager[self.symbol].close.iloc[-1]
        self.update(f"{price:.2f}")

class SymbolTicker(Static):
    """
    Widget representing a single stock symbol, including price display and plot.

    Contains a remove button, a real-time price display, and a plot of recent price history.
    Can be dynamically added or removed from the UI.

    Args:
        symbol (str): The symbol to display.
        stock_manager (StockManager): Reference to the stock manager.
    """

    def __init__(self, symbol, stock_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.symbol = symbol  # Symbol to display
        self.stock_manager = stock_manager  # Reference to StockManager

    def compose(self) -> ComposeResult:
        """
        Compose the widgets for the symbol ticker.

        Includes a remove button, price display, and a plot widget.
        """
        with HorizontalGroup():
            yield Button(f"Remove Symbol {self.symbol}", id="remove")  # Remove button
            yield TickerPriceDisplay(self.symbol, self.stock_manager, id=f"{Clean_symbol(self.symbol)}")  # Price display
        yield PlotWidget(id="plot")  # Plot widget

    def on_mount(self) -> None:
        """
        Plot the symbol's historical data and update the price display on mount.

        Initializes the plot with the symbol's closing prices and updates the price display.
        """
        plot = self.query_one(PlotWidget)
        symbol_data = self.stock_manager[self.symbol]
        plot.plot(x=symbol_data.datetime, y=symbol_data.close, hires_mode=HiResMode.BRAILLE)
        sticker = self.query_one(f"#{Clean_symbol(self.symbol)}")
        sticker.update(f"{self.stock_manager[self.symbol].close.iloc[-1]:.2f}")

    @on(Button.Pressed, "#remove")
    def remove_symbol(self) -> None:
        """
        Remove this symbol widget from the UI when the remove button is pressed.
        """
        self.remove()

class SymbolWatcher(App):
    """
    Main application class for the Symbol Watcher.

    Manages the overall UI, event handling, and coordination between widgets.
    Handles loading holdings, creating stock data objects, and responding to user actions
    such as adding symbols, toggling the overview, and displaying help.

    Attributes:
        TITLE (str): The application title.
        SUB_TITLE (str): The application subtitle/version.
        CSS_PATH (str): Path to the CSS file for styling.
        BINDINGS (list): Key bindings for user actions.
        stock_manager (StockManager): The manager for all stock data.
    """

    TITLE = "Symbol Watcher 3"
    SUB_TITLE = "0.1"
    
    CSS_PATH = "style.tcss"  # Path to CSS file
    BINDINGS = [
        ("a", "add_symbols", "Add symbols"),
        ("s", "toggle_overview", "Toggle Overview"),
        ("h", "toggle_help", "Help")
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stock_manager = StockManager() # Create stock manager
        self.currency_convert = CurrencyConvert(self.stock_manager) # Create a Currency Converter 
        symbols = create_symbols()  # Create symbol data objects
        for symbol in symbols:
            self.stock_manager.add_stock(symbol)  # Add to manager

    def compose(self) -> ComposeResult:
        """
        Compose the main application widgets.

        Includes the header, portfolio overview, symbol tickers container, and footer.
        """
        yield Header(show_clock=True)  # Header with clock
        yield PortfolioOverview(self.stock_manager, self.currency_convert, classes="-hidden")  # Portfolio overview
        with ScrollableContainer(id="Symbols"): # Container for symbol tickers
            pass  
        yield Footer()  # Footer
    
    def on_mount(self):
        """
        Set the application theme when the app is mounted.
        """
        self.theme = "nord"

    def action_toggle_overview(self) -> None:
        """
        Toggle the visibility of the portfolio overview widget.
        """
        self.query_one(PortfolioOverview).toggle_class("-hidden")

    def action_add_symbols(self):
        """
        Add symbol ticker widgets to the UI for each holding.

        Dynamically mounts a SymbolTicker for each symbol in the stock manager.
        """
        print("Creating Symbols with plots n stuff")
        for symbol in self.stock_manager.stocks:
            symbolticker = SymbolTicker(self.stock_manager[symbol].symbol, self.stock_manager)
            container = self.query_one("#Symbols")
            container.mount(symbolticker)
            symbolticker.scroll_visible()

    def action_toggle_help(self):
        """
        Display the help screen as a modal overlay.
        """
        self.push_screen(HelpScreen())

if __name__ == "__main__":
    # Load holdings
    HOLDINGS = load_holdings()
    if not HOLDINGS:
        print("No holdings found. Please ensure 'holdings.json' exists and contains valid JSON data.")
    else:
        print(HOLDINGS)
        
    # Load settings
    PERIOD = load_settings().get("PERIOD")  # Timespan of data to fetch, default to "1d" if not set
    INTERVAL = load_settings().get("INTERVAL")  # Data granularity
    UPDATE_INTERVAL = load_settings().get("UPDATE_INTERVAL")  # How often to fetch prices (in seconds), min 60
    LOCAL_CURRENCY = load_settings().get("LOCAL_CURRENCY")  # Local currency for conversion

    # Run the app
    SymbolWatcher().run() 