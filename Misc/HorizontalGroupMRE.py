from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup
from textual.widgets import Label

### TEST DATA ###
HOLDINGS = {
    "SAAB-B.ST": [1, 500],
    "SSAB-B.ST": [1, 500],
    "^OMX": [0, 0],
    "MSFT": [1, 500],
    "AAPL": [0, 0],
    "AMZN": [0,1]
}
price = 10


class SymbolWatcher(App):
    CSS_PATH = "style.css"
    BINDINGS = [
        ("a", "add_symbols", "Add symbols"),
        ("t", "toggle_dark", "Toggle dark mode")
    ]

    def compose(self) -> ComposeResult:
            """Widgets for Portfolio overview"""
            total = 0
            total_change = 0
            with HorizontalGroup():
                for symbol in HOLDINGS.keys():
                    with VerticalGroup():
                        yield Label(f"{symbol}")
                        with HorizontalGroup():
                            yield Label(f"Close: {price}")
                        with VerticalGroup():
                            actualvalue = price * HOLDINGS[symbol][0]
                            total += actualvalue
                            yield Label(f"Actual: {str(actualvalue)}")
                        with VerticalGroup():
                            q = HOLDINGS[symbol][0]
                            v = HOLDINGS[symbol][1]
                            purchased_value = q * v
                            change = actualvalue - purchased_value
                            total_change += change
                            yield Label(str(change))
            total_change
            yield Label(f"TOTAL WORTH: {total} ::: TOTAL CHANGE: {total_change}")
                        
                        
if __name__ == "__main__":
    SymbolWatcher().run()