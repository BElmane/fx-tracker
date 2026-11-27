"""Regression tests: tricky cases that already work and must keep working."""

from datetime import date

import pytest

from fx_tracker.caching_rate_provider import CachingRateProvider
from fx_tracker.errors import InvalidCurrencyError, RateServiceUnavailableError, WatchlistStorageError
from fx_tracker.frankfurter_client import FrankfurterClient
from fx_tracker.rate_service import RateService
from fx_tracker.watchlist_service import WatchlistService
from fx_tracker.watchlist_store import JsonWatchlistStore
from tests.fakes import HTTP_OK, FakeRateProvider, FakeResponse, FakeSession, FakeWatchlistStore

TEST_URL = "https://test.api"
API_ERROR_CODE = 422


class BadJsonResponse(FakeResponse):
    """A response whose body is not valid JSON."""

    def json(self):
        raise ValueError("not JSON")


def make_client(session):
    return FrankfurterClient(session=session, base_url=TEST_URL)


def test_same_currency_with_different_case_and_spaces_is_rejected():
    """Codes must be cleaned BEFORE they are compared."""
    session = FakeSession(response=FakeResponse(HTTP_OK, {}))
    service = RateService(make_client(session))
    with pytest.raises(InvalidCurrencyError):
        service.get_rate(" usd ", "USD")
    assert session.last_url is None


def test_error_without_json_body_still_gives_a_message():
    """If the API sends an error that is not JSON, we still show a message."""
    session = FakeSession(response=BadJsonResponse(API_ERROR_CODE, None))
    with pytest.raises(InvalidCurrencyError, match="Invalid currency."):
        make_client(session).get_rate("USD", "ABC")


def test_good_status_with_bad_json_does_not_crash():
    """A broken success response becomes our own error, not a crash."""
    session = FakeSession(response=BadJsonResponse(HTTP_OK, None))
    with pytest.raises(RateServiceUnavailableError):
        make_client(session).get_rate("USD", "EUR")


def test_currency_without_symbol_still_works():
    """Some currencies may not have a symbol in the API data."""
    data = [{"iso_code": "XAU", "name": "Gold"}]
    session = FakeSession(response=FakeResponse(HTTP_OK, data))
    currencies = make_client(session).get_currencies()
    assert currencies[0].symbol == ""


def test_rate_sent_as_text_is_turned_into_a_number():
    """The rate must always be a float, even if the API sends it as text."""
    data = {"date": "2026-10-14", "base": "USD", "quote": "EUR", "rate": "0.89"}
    session = FakeSession(response=FakeResponse(HTTP_OK, data))
    rate = make_client(session).get_rate("USD", "EUR")
    assert rate.rate == 0.89


def test_empty_history_does_not_crash():
    """If the API has no history for a pair, we get an empty result."""
    session = FakeSession(response=FakeResponse(HTTP_OK, []))
    history = make_client(session).get_history("USD", "MAD", date(2026, 11, 1))
    assert history == ()


def test_swapped_pairs_are_different_watchlist_items():
    """USD/MAD and MAD/USD are two different pairs, so both are allowed."""
    watchlist = WatchlistService(FakeWatchlistStore(), RateService(FakeRateProvider()))
    watchlist.add("USD", "MAD")
    watchlist.add("MAD", "USD")
    assert [item.pair for item in watchlist.items()] == ["USD/MAD", "MAD/USD"]


def test_watchlist_file_with_unknown_field_raises_our_own_error(tmp_path):
    """A file with an extra field we don't know must not crash the app."""
    path = tmp_path / "watchlist.json"
    path.write_text('[{"base": "USD", "quote": "MAD", "color": "red"}]', encoding="utf-8")
    with pytest.raises(WatchlistStorageError):
        JsonWatchlistStore(path).load()


def test_proxy_keeps_swapped_pairs_separate():
    """The cache key is the pair in order, so USD/MAD never answers for MAD/USD."""
    proxy = CachingRateProvider(FakeRateProvider())
    usd_mad = proxy.get_rate("USD", "MAD")
    mad_usd = proxy.get_rate("MAD", "USD")
    assert (usd_mad.base, mad_usd.base) == ("USD", "MAD")