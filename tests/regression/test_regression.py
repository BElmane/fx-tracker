"""Regression tests: tricky cases that already work and must keep working."""

import pytest

from fx_tracker.errors import InvalidCurrencyError, RateServiceUnavailableError
from fx_tracker.frankfurter_client import FrankfurterClient
from fx_tracker.rate_service import RateService
from tests.fakes import HTTP_OK, FakeResponse, FakeSession

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
    