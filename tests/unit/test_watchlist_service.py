"""Unit tests for WatchlistService, using a fake store and a fake provider."""

import pytest

from fx_tracker.errors import InvalidCurrencyError, InvalidTargetError, WatchlistError
from fx_tracker.models import WatchItem
from fx_tracker.rate_service import RateService
from fx_tracker.watchlist_service import WatchlistService
from tests.fakes import FAKE_RATE, UNSUPPORTED_CODE, FakeRateProvider, FakeWatchlistStore


def make_watchlist(items=()):
    """Build a WatchlistService with fakes injected (no file, no internet)."""
    return WatchlistService(FakeWatchlistStore(items), RateService(FakeRateProvider()))


def test_add_cleans_codes_and_saves_the_pair():
    watchlist = make_watchlist()
    item = watchlist.add(" usd ", "mad")
    assert item.pair == "USD/MAD"
    assert watchlist.items() == (item,)


def test_add_keeps_the_target():
    watchlist = make_watchlist()
    watchlist.add("USD", "MAD", 10.0)
    assert watchlist.items()[0].target == 10.0


def test_add_blocks_duplicates():
    watchlist = make_watchlist((WatchItem("USD", "MAD"),))
    with pytest.raises(WatchlistError):
        watchlist.add("usd", "mad")


def test_add_blocks_pairs_the_api_does_not_support():
    watchlist = make_watchlist()
    with pytest.raises(InvalidCurrencyError):
        watchlist.add("USD", UNSUPPORTED_CODE)
    assert watchlist.items() == ()


def test_add_blocks_the_same_currency_twice():
    watchlist = make_watchlist()
    with pytest.raises(InvalidCurrencyError):
        watchlist.add("USD", "USD")


@pytest.mark.parametrize("bad_target", [0, -1])
def test_add_blocks_bad_targets(bad_target):
    watchlist = make_watchlist()
    with pytest.raises(InvalidTargetError):
        watchlist.add("USD", "MAD", bad_target)


def test_remove_takes_the_pair_out():
    watchlist = make_watchlist((WatchItem("USD", "MAD"), WatchItem("EUR", "USD")))
    watchlist.remove("USD/MAD")
    assert [item.pair for item in watchlist.items()] == ["EUR/USD"]


def test_remove_missing_pair_raises_an_error():
    watchlist = make_watchlist()
    with pytest.raises(WatchlistError):
        watchlist.remove("USD/MAD")


def test_set_target_changes_only_that_pair():
    watchlist = make_watchlist((WatchItem("USD", "MAD"), WatchItem("EUR", "USD", 1.2)))
    watchlist.set_target("USD/MAD", 10.0)
    targets = {item.pair: item.target for item in watchlist.items()}
    assert targets == {"USD/MAD": 10.0, "EUR/USD": 1.2}


def test_set_target_none_removes_the_target():
    watchlist = make_watchlist((WatchItem("USD", "MAD", 10.0),))
    watchlist.set_target("USD/MAD", None)
    assert watchlist.items()[0].target is None


def test_set_target_on_missing_pair_raises_an_error():
    watchlist = make_watchlist()
    with pytest.raises(WatchlistError):
        watchlist.set_target("USD/MAD", 10.0)


def test_set_target_blocks_bad_targets():
    watchlist = make_watchlist((WatchItem("USD", "MAD"),))
    with pytest.raises(InvalidTargetError):
        watchlist.set_target("USD/MAD", -5)


def test_check_alerts_finds_only_targets_that_were_reached():
    watchlist = make_watchlist(
        (
            WatchItem("USD", "MAD", 0.4, "above"),
            WatchItem("EUR", "USD", 0.6, "above"),
            WatchItem("GBP", "USD", 0.6, "below"),
            WatchItem("JPY", "USD"),
        )
    )
    alerts = watchlist.check_alerts()
    assert [alert.item.pair for alert in alerts] == ["USD/MAD", "GBP/USD"]


def test_check_alerts_includes_the_current_rate():
    watchlist = make_watchlist((WatchItem("USD", "MAD", 0.4, "above"),))
    alert = watchlist.check_alerts()[0]
    assert alert.rate.rate == FAKE_RATE


def test_check_alerts_is_empty_when_no_targets_are_set():
    watchlist = make_watchlist((WatchItem("USD", "MAD"), WatchItem("EUR", "USD")))
    assert watchlist.check_alerts() == ()


def test_add_blocks_unknown_direction():
    watchlist = make_watchlist()
    with pytest.raises(InvalidTargetError):
        watchlist.add("USD", "MAD", 10.0, "sideways")


def test_set_target_can_change_the_direction():
    watchlist = make_watchlist((WatchItem("USD", "MAD", 10.0, "above"),))
    watchlist.set_target("USD/MAD", 9.5, "below")
    item = watchlist.items()[0]
    assert (item.target, item.direction) == (9.5, "below")