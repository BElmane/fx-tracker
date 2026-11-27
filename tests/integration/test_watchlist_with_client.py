"""Integration tests: the watchlist, the file store, the proxy, and the API client together."""

import pytest

from fx_tracker.caching_rate_provider import CachingRateProvider
from fx_tracker.errors import InvalidCurrencyError
from fx_tracker.frankfurter_client import FrankfurterClient
from fx_tracker.rate_service import RateService
from fx_tracker.watchlist_service import WatchlistService
from fx_tracker.watchlist_store import JsonWatchlistStore
from tests.fakes import HTTP_OK, FakeResponse, FakeSession

TEST_URL = "https://test.api"
API_ERROR_CODE = 422
USD_MAD = {"date": "2026-11-27", "base": "USD", "quote": "MAD", "rate": 10.0}


class CountingSession(FakeSession):
    """A fake session that counts how many web requests were sent."""

    def __init__(self, response):
        super().__init__(response=response)
        self.calls = 0

    def get(self, url, timeout):
        self.calls += 1
        return super().get(url, timeout)


def make_watchlist(session, path):
    """Build the real chain. Only the internet (the session) is fake."""
    client = FrankfurterClient(session=session, base_url=TEST_URL)
    rate_service = RateService(CachingRateProvider(client))
    return WatchlistService(JsonWatchlistStore(path), rate_service)


def test_added_pair_is_saved_in_the_real_file(tmp_path):
    path = tmp_path / "watchlist.json"
    session = FakeSession(response=FakeResponse(HTTP_OK, USD_MAD))
    make_watchlist(session, path).add(" usd ", "mad", 9.5, "above")
    saved = JsonWatchlistStore(path).load()
    assert (saved[0].pair, saved[0].target) == ("USD/MAD", 9.5)


def test_alert_goes_through_the_whole_chain(tmp_path):
    session = FakeSession(response=FakeResponse(HTTP_OK, USD_MAD))
    watchlist = make_watchlist(session, tmp_path / "watchlist.json")
    watchlist.add("USD", "MAD", 9.5, "above")
    alerts = watchlist.check_alerts()
    assert alerts[0].rate.rate == 10.0


def test_proxy_saves_a_web_request_in_the_real_chain(tmp_path):
    session = CountingSession(response=FakeResponse(HTTP_OK, USD_MAD))
    watchlist = make_watchlist(session, tmp_path / "watchlist.json")
    watchlist.add("USD", "MAD", 9.5, "above")
    watchlist.check_alerts()
    assert session.calls == 1


def test_api_error_on_add_saves_nothing(tmp_path):
    path = tmp_path / "watchlist.json"
    error_data = {"status": API_ERROR_CODE, "message": "invalid currency: XYZ"}
    session = FakeSession(response=FakeResponse(API_ERROR_CODE, error_data))
    with pytest.raises(InvalidCurrencyError):
        make_watchlist(session, path).add("USD", "XYZ")
    assert not path.exists()