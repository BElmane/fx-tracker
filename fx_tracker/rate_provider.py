"""The contract that every exchange-rate source must follow."""

from abc import ABC, abstractmethod

from fx_tracker.models import Currency, ExchangeRate


class RateProvider(ABC):
    """Any rate source must have these two methods."""

    @abstractmethod
    def get_currencies(self) -> tuple[Currency, ...]:
        """Return all supported currencies."""

    @abstractmethod
    def get_rate(self, base: str, quote: str) -> ExchangeRate:
        """Return the latest rate from base to quote."""
        