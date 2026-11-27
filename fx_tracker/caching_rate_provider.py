"""Proxy pattern: remembers rates for a few minutes so the API isn't called again and again."""

import time
from datetime import date

from fx_tracker.config import CACHE_SECONDS
from fx_tracker.models import Currency, ExchangeRate
from fx_tracker.rate_provider import RateProvider


class CachingRateProvider(RateProvider):
    """Sits in front of a real provider and reuses recent answers."""

    def __init__(self, real_provider: RateProvider, max_age_seconds=CACHE_SECONDS, clock=time.monotonic):
        self._real_provider = real_provider
        self._max_age_seconds = max_age_seconds
        self._clock = clock
        self._currencies = None
        self._rates = {}

    def get_currencies(self) -> tuple[Currency, ...]:
        """The currency list almost never changes, so get it only once."""
        if self._currencies is None:
            self._currencies = self._real_provider.get_currencies()
        return self._currencies

    def get_rate(self, base: str, quote: str) -> ExchangeRate:
        """Return a saved rate if it's fresh. Otherwise ask the real provider."""
        key = (base, quote)
        now = self._clock()
        saved = self._rates.get(key)
        if saved is not None:
            saved_at, rate = saved
            if now - saved_at < self._max_age_seconds:
                return rate
        rate = self._real_provider.get_rate(base, quote)
        self._rates[key] = (now, rate)
        return rate

    def get_history(self, base: str, quote: str, start: date) -> tuple[ExchangeRate, ...]:
        """History is only asked for once per click, so pass it straight through."""
        return self._real_provider.get_history(base, quote, start)