"""Rules for the user's watchlist: add pairs, remove pairs, and set target rates."""

from dataclasses import replace

from fx_tracker.errors import InvalidTargetError, WatchlistError
from fx_tracker.models import WatchItem
from fx_tracker.rate_service import RateService
from fx_tracker.watchlist_store import WatchlistStore


class WatchlistService:
    """Manages the watchlist. The store and the rate service are passed in."""

    def __init__(self, store: WatchlistStore, rate_service: RateService):
        self._store = store
        self._rate_service = rate_service

    def items(self) -> tuple[WatchItem, ...]:
        """Return every pair in the watchlist."""
        return self._store.load()

    def add(self, base: str, quote: str, target: float | None = None) -> WatchItem:
        """Add a pair. The rate service checks the codes and that the API supports them."""
        self._check_target(target)
        rate = self._rate_service.get_rate(base, quote)
        item = WatchItem(rate.base, rate.quote, target)
        items = self._store.load()
        if any(existing.pair == item.pair for existing in items):
            raise WatchlistError(f"{item.pair} is already in your watchlist.")
        self._store.save(items + (item,))
        return item

    def remove(self, pair: str) -> None:
        """Remove a pair like 'USD/MAD'."""
        items = self._store.load()
        self._require_pair(items, pair)
        self._store.save(tuple(item for item in items if item.pair != pair))

    def set_target(self, pair: str, target: float | None) -> None:
        """Set or change the target rate of a pair. None removes the target."""
        self._check_target(target)
        items = self._store.load()
        self._require_pair(items, pair)
        self._store.save(
            tuple(replace(item, target=target) if item.pair == pair else item for item in items)
        )

    @staticmethod
    def _check_target(target: float | None) -> None:
        """A target must be more than 0, or None for no target."""
        if target is not None and target <= 0:
            raise InvalidTargetError("The target rate must be greater than 0.")

    @staticmethod
    def _require_pair(items: tuple[WatchItem, ...], pair: str) -> None:
        """Raise an error if the pair is not in the watchlist."""
        if not any(item.pair == pair for item in items):
            raise WatchlistError(f"{pair} is not in your watchlist.")
        