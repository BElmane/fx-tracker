"""Unit tests for FrankfurterClient, using a fake session (no internet)."""

import pytest
import requests

from fx_tracker.errors import InvalidCurrencyError, RateServiceUnavailableError
from fx_tracker.frankfurter_client import FrankfurterClient
from tests.fakes import HTTP_OK, FakeResponse, FakeSession

TEST_URL = "https://test.api"




def make_client(session):
    return FrankfurterClient(session=session, base_url=TEST_URL)


def test_get_rate_builds_url_and_reads_data():
    data = {"date": "2026-10-14", "base": "USD", "quote": "EUR", "rate": 0.89}
    session = FakeSession(response=FakeResponse(HTTP_OK, data))
    rate = make_client(session).get_rate("USD", "EUR")
    assert session.last_url == f"{TEST_URL}/rate/usd/eur"
    assert (rate.base, rate.quote, rate.rate) == ("USD", "EUR", 0.89)


def test_get_currencies_reads_list():
    data = [{"iso_code": "EUR", "name": "Euro", "symbol": "€"}]
    session = FakeSession(response=FakeResponse(HTTP_OK, data))
    currencies = make_client(session).get_currencies()
    assert currencies[0].code == "EUR"
    assert currencies[0].symbol == "€"


@pytest.mark.parametrize("status_code", [400, 404, 422])
def test_bad_request_raises_invalid_currency(status_code):
    data = {"status": status_code, "message": "invalid currency: ABC"}
    session = FakeSession(response=FakeResponse(status_code, data))
    with pytest.raises(InvalidCurrencyError, match="ABC"):
        make_client(session).get_rate("USD", "ABC")


def test_server_error_raises_unavailable():
    session = FakeSession(response=FakeResponse(500, {}))
    with pytest.raises(RateServiceUnavailableError):
        make_client(session).get_rate("USD", "EUR")


@pytest.mark.parametrize("network_error", [requests.ConnectionError(), requests.Timeout()])
def test_network_problem_raises_unavailable(network_error):
    session = FakeSession(error=network_error)
    with pytest.raises(RateServiceUnavailableError):
        make_client(session).get_rate("USD", "EUR")