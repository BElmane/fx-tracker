"""Fake objects shared by the tests. They pretend to be the internet and the file."""

from fx_tracker.errors import InvalidCurrencyError
from fx_tracker.models import Currency, ExchangeRate
from fx_tracker.rate_provider import RateProvider
from fx_tracker.watchlist_store import WatchlistStore

HTTP_OK = 200
FAKE_RATE = 0.5
FAKE_DATE = "2026-10-14"
UNSUPPORTED_CODE = "XYZ"


class FakeResponse:
    """Pretends to be a response from the API."""

    def __init__(self, status_code, data):
        self.status_code = status_code
        self.ok = status_code == HTTP_OK
        self._data = data

    def json(self):
        return self._data


class FakeSession:
    """Pretends to send web requests. Remembers the last URL."""

    def __init__(self, response=None, error=None):
        self._response = response
        self._error = error
        self.last_url = None

    def get(self, url, timeout):
        self.last_url = url
        if self._error:
            raise self._error
        return self._response


class FakeRateProvider(RateProvider):
    """Pretends to be the API. Always gives the same answers."""

    def __init__(self):
        self.currency_calls = 0
        self.last_history_pair = None
        self.last_history_start = None

    def get_currencies(self):
        self.currency_calls += 1
        return (Currency("USD", "US Dollar"), Currency("EUR", "Euro"))

    def get_rate(self, base, quote):
        if UNSUPPORTED_CODE in (base, quote):
            raise InvalidCurrencyError(f"invalid currency: {UNSUPPORTED_CODE}")
        return ExchangeRate(base, quote, FAKE_RATE, FAKE_DATE)

    def get_history(self, base, quote, start):
        self.last_history_pair = (base, quote)
        self.last_history_start = start
        return (
            ExchangeRate(base, quote, FAKE_RATE, "2026-11-01"),
            ExchangeRate(base, quote, FAKE_RATE, "2026-11-02"),
        )


class FakeWatchlistStore(WatchlistStore):
    """Pretends to be the watchlist file. Keeps the list in memory."""

    def __init__(self, items=()):
        self._items = tuple(items)

    def load(self):
        return self._items

    def save(self, items):
        self._items = tuple(items)