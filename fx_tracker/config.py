"""Settings for FX Tracker. Fixed values live here, not inside the code."""

API_BASE_URL = "https://api.frankfurter.dev/v2"
REQUEST_TIMEOUT_SECONDS = 10
DEFAULT_FROM_CURRENCY = "USD"
DEFAULT_TO_CURRENCY = "EUR"
DEFAULT_HISTORY_DAYS = 30
HISTORY_DAY_OPTIONS = (7, 30, 90)
WATCHLIST_FILE = "watchlist.json"
CACHE_SECONDS = 300