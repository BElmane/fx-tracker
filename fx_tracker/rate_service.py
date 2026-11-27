"""App rules for FX Tracker. Works with any RateProvider passed in."""

from datetime import date, timedelta

from fx_tracker.config import DEFAULT_HISTORY_DAYS
from fx_tracker.errors import InvalidAmountError, InvalidCurrencyError, InvalidPeriodError
from fx_tracker.models import Currency, ExchangeRate
from fx_tracker.rate_provider import RateProvider

CURRENCY_CODE_LENGTH = 3


class RateService:
    """Checks user input and gets rates from the provider."""

    def __init__(self, provider: RateProvider, today=date.today):
        self._provider = provider
        self._today = today
        self._currencies = None

    def list_currencies(self) -> tuple[Currency, ...]:
        """Return supported currencies sorted by code. Downloads only once."""
        if self._currencies is None:
            self._currencies = tuple(
                sorted(self._provider.get_currencies(), key=lambda currency: currency.code)
            )
        return self._currencies

    def get_rate(self, base: str, quote: str) -> ExchangeRate:
        """Clean and check both codes, then get the rate."""
        base, quote = self._clean_pair(base, quote)
        return self._provider.get_rate(base, quote)

    def convert(self, base: str, quote: str, amount: float) -> tuple[ExchangeRate, float]:
        """Return the rate and the converted amount."""
        if amount <= 0:
            raise InvalidAmountError("Enter an amount greater than 0.")
        rate = self.get_rate(base, quote)
        return rate, rate.convert(amount)

    def get_history(
        self, base: str, quote: str, days: int = DEFAULT_HISTORY_DAYS
    ) -> tuple[ExchangeRate, ...]:
        """Return daily rates for the last `days` days, oldest first."""
        if days <= 0:
            raise InvalidPeriodError("Pick at least 1 day of history.")
        base, quote = self._clean_pair(base, quote)
        start = self._today() - timedelta(days=days)
        return self._provider.get_history(base, quote, start)

    def _clean_pair(self, base: str, quote: str) -> tuple[str, str]:
        """Clean both codes and make sure they are different."""
        base = self._clean_code(base)
        quote = self._clean_code(quote)
        if base == quote:
            raise InvalidCurrencyError("Pick two different currencies.")
        return base, quote

    @staticmethod
    def _clean_code(code: str) -> str:
        """Turn ' usd ' into 'USD'. Reject anything that isn't 3 letters."""
        cleaned = (code or "").strip().upper()
        if len(cleaned) != CURRENCY_CODE_LENGTH or not cleaned.isalpha():
            raise InvalidCurrencyError(f"'{code}' is not a valid currency code.")
        return cleaned