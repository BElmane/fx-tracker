"""Unit tests for JsonWatchlistStore, using a temporary folder."""

import json

import pytest

from fx_tracker.errors import WatchlistStorageError
from fx_tracker.models import WatchItem
from fx_tracker.watchlist_store import JsonWatchlistStore

ITEMS = (WatchItem("USD", "MAD", 10.0), WatchItem("EUR", "USD"))


def test_missing_file_gives_empty_watchlist(tmp_path):
    store = JsonWatchlistStore(tmp_path / "watchlist.json")
    assert store.load() == ()


def test_saved_items_load_back_the_same(tmp_path):
    store = JsonWatchlistStore(tmp_path / "watchlist.json")
    store.save(ITEMS)
    assert store.load() == ITEMS


def test_saved_file_is_readable_json(tmp_path):
    path = tmp_path / "watchlist.json"
    JsonWatchlistStore(path).save(ITEMS)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data[0] == {"base": "USD", "quote": "MAD", "target": 10.0, "direction": "above"}
    assert data[1]["target"] is None


def test_old_file_without_direction_still_loads(tmp_path):
    path = tmp_path / "watchlist.json"
    path.write_text('[{"base": "USD", "quote": "MAD", "target": 10.0}]', encoding="utf-8")
    assert JsonWatchlistStore(path).load()[0].direction == "above"


def test_broken_file_raises_our_own_error(tmp_path):
    path = tmp_path / "watchlist.json"
    path.write_text("this is not json", encoding="utf-8")
    with pytest.raises(WatchlistStorageError):
        JsonWatchlistStore(path).load()