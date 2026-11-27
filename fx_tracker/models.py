"""Data classes for FX Tracker."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Currency:
    """One supported currency, like USD or EUR."""

    code: str
    name: str
    symbol: str = ""


@dataclass(frozen=True)
class ExchangeRate:
    """The rate between two currencies on one date."""

    base: str
    quote: str
    rate: float
    date: str

    def convert(self, amount: float) -> float:
        """Return how much `amount` of base is worth in quote."""
        return amount * self.rate


@dataclass(frozen=True)
class WatchItem:
    """One currency pair the user wants to track, with an optional target rate."""

    base: str
    quote: str
    target: float | None = None

    @property
    def pair(self) -> str:
        """Return a short name like 'USD/MAD'."""
        return f"{self.base}/{self.quote}"