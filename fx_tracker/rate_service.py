"""App rules for FX Tracker. Works with any RateProvider passed in."""

from fx_tracker.errors import InvalidAmountError, InvalidCurrencyError
from fx_tracker.models import Currency, ExchangeRate
from fx_tracker.rate_provider import RateProvider

CURRENCY_CODE_LENGTH = 3


class RateService:
    """Checks user input and gets rates from the provider."""

    def __init__(self, provider: RateProvider):
        self._provider = provider
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
        base = self._clean_code(base)
        quote = self._clean_code(quote)
        if base == quote:
            raise InvalidCurrencyError("Pick two different currencies.")
        return self._provider.get_rate(base, quote)

    def convert(self, base: str, quote: str, amount: float) -> tuple[ExchangeRate, float]:
        """Return the rate and the converted amount."""
        if amount <= 0:
            raise InvalidAmountError("Enter an amount greater than 0.")
        rate = self.get_rate(base, quote)
        return rate, rate.convert(amount)

    @staticmethod
    def _clean_code(code: str) -> str:
        """Turn ' usd ' into 'USD'. Reject anything that isn't 3 letters."""
        cleaned = (code or "").strip().upper()
        if len(cleaned) != CURRENCY_CODE_LENGTH or not cleaned.isalpha():
            raise InvalidCurrencyError(f"'{code}' is not a valid currency code.")
        return cleaned