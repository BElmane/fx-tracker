"""Saving and loading the watchlist."""

import json
from abc import ABC, abstractmethod
from dataclasses import asdict
from pathlib import Path

from fx_tracker.config import WATCHLIST_FILE
from fx_tracker.errors import WatchlistStorageError
from fx_tracker.models import WatchItem


class WatchlistStore(ABC):
    """The contract for anything that can save and load the watchlist."""

    @abstractmethod
    def load(self) -> tuple[WatchItem, ...]:
        """Return the saved watchlist. Empty if nothing is saved yet."""

    @abstractmethod
    def save(self, items: tuple[WatchItem, ...]) -> None:
        """Save the whole watchlist, replacing what was there."""


class JsonWatchlistStore(WatchlistStore):
    """Saves the watchlist in a JSON file."""

    def __init__(self, path=WATCHLIST_FILE):
        self._path = Path(path)

    def load(self) -> tuple[WatchItem, ...]:
        if not self._path.exists():
            return ()
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            return tuple(WatchItem(**item) for item in data)
        except (ValueError, TypeError) as error:
            raise WatchlistStorageError("Your saved watchlist could not be read.") from error

    def save(self, items: tuple[WatchItem, ...]) -> None:
        data = [asdict(item) for item in items]
        self._path.write_text(json.dumps(data, indent=2), encoding="utf-8")