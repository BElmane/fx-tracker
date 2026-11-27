"""Rules for the user's watchlist: add pairs, remove pairs, set targets, and check alerts."""

from dataclasses import replace

from fx_tracker.alert_rules import ALERT_RULES, DEFAULT_DIRECTION
from fx_tracker.errors import InvalidTargetError, WatchlistError
from fx_tracker.models import Alert, WatchItem
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

    def add(
        self,
        base: str,
        quote: str,
        target: float | None = None,
        direction: str = DEFAULT_DIRECTION,
    ) -> WatchItem:
        """Add a pair. The rate service checks the codes and that the API supports them."""
        self._check_target(target)
        self._check_direction(direction)
        rate = self._rate_service.get_rate(base, quote)
        item = WatchItem(rate.base, rate.quote, target, direction)
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

    def set_target(
        self, pair: str, target: float | None, direction: str = DEFAULT_DIRECTION
    ) -> None:
        """Set or change the target of a pair. None removes the target."""
        self._check_target(target)
        self._check_direction(direction)
        items = self._store.load()
        self._require_pair(items, pair)
        self._store.save(
            tuple(
                replace(item, target=target, direction=direction) if item.pair == pair else item
                for item in items
            )
        )

    def check_alerts(self) -> tuple[Alert, ...]:
        """Return an alert for every pair whose target has been reached."""
        alerts = []
        for item in self._store.load():
            if item.target is None:
                continue
            rate = self._rate_service.get_rate(item.base, item.quote)
            rule = ALERT_RULES[item.direction]
            if rule.is_met(rate.rate, item.target):
                alerts.append(Alert(item, rate))
        return tuple(alerts)

    @staticmethod
    def _check_target(target: float | None) -> None:
        """A target must be more than 0, or None for no target."""
        if target is not None and target <= 0:
            raise InvalidTargetError("The target rate must be greater than 0.")

    @staticmethod
    def _check_direction(direction: str) -> None:
        """The direction must be one of the known alert rules."""
        if direction not in ALERT_RULES:
            raise InvalidTargetError(f"Pick one of: {', '.join(ALERT_RULES)}.")

    @staticmethod
    def _require_pair(items: tuple[WatchItem, ...], pair: str) -> None:
        """Raise an error if the pair is not in the watchlist."""
        if not any(item.pair == pair for item in items):
            raise WatchlistError(f"{pair} is not in your watchlist.")