import json
def load_settings(filename="settings.json"):
    """
    Load application settings from a JSON file.

    Reads the specified JSON file to load user-configurable settings such as PERIOD, INTERVAL, and UPDATE_INTERVAL.
    These settings control the timespan of data to fetch, the data granularity, and how often prices are updated.
    If the file does not exist, returns an empty dictionary.

    Args:
        filename (str): The path to the JSON file containing application settings.

    Returns:
        dict: A dictionary containing settings for PERIOD, INTERVAL, and UPDATE_INTERVAL.
    """
    try:
        with open(filename, "r") as f:
            settings = json.load(f)
            # Only grab specific entries if they exist
            result = {}
            for key in ["PERIOD", "INTERVAL", "UPDATE_INTERVAL", "LOCAL_CURRENCY"]:
                if key in settings:
                    result[key] = settings[key]
            return result
    except FileNotFoundError:
        return {}

### SETTINGS ### MOVING THESE TO JSON SOON.
print(load_settings().get("PERIOD"))  # Timespan of data to fetch, default to "1d" if not set
