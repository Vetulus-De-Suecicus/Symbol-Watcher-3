import json

def load_holdings(filename="holdings.json"):
    """Load holdings from a JSON file."""
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # If file doesn't exist, return empty dict or provide a default
        return {}

HOLDINGS = load_holdings()

if not HOLDINGS:
    print("No holdings found. Please ensure 'holdings.json' exists and contains valid JSON data.")
else:
    print(HOLDINGS)
