from textual import on
from textual_plot import PlotWidget
from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer, HorizontalGroup
from textual.widgets import Label, Header, Footer, Static, Button

symbols = ["SAAB", "MSFT", "AAPL", "AMZN", "IPCO"]

class PortfolioOverview(Static):
    def compose(self) -> ComposeResult:
        """Widgets for Portfolio overview"""
        with HorizontalGroup(id="symbolsgroup"):
            for id, symbol in enumerate(symbols):
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

    def on_mount(self) -> None:
        plot = self.query_one(PlotWidget)
        plot.plot(x=[0, 1, 2, 3, 4], y=[0, 1, 4, 9, 16])

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
        symbolticker = SymbolTicker()
        container = self.query_one("#Symbols")
        container.mount(symbolticker)
        symbolticker.scroll_visible()

if __name__ == "__main__":
    SymbolWatcher().run()