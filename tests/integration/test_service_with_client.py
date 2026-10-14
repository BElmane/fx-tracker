"""Integration tests: RateService and FrankfurterClient working together."""

import pytest
import requests

from fx_tracker.errors import InvalidCurrencyError, RateServiceUnavailableError
from fx_tracker.frankfurter_client import FrankfurterClient
from fx_tracker.rate_service import RateService
from tests.fakes import HTTP_OK, FakeResponse, FakeSession

TEST_URL = "https://test.api"
API_ERROR_CODE = 422


def make_service(session):
    return RateService(FrankfurterClient(session=session, base_url=TEST_URL))


def test_messy_input_goes_through_to_the_api_and_back():
    data = {"date": "2026-10-14", "base": "USD", "quote": "MAD", "rate": 10.0}
    session = FakeSession(response=FakeResponse(HTTP_OK, data))
    rate, converted = make_service(session).convert(" usd ", "mad", 50)
    assert session.last_url == f"{TEST_URL}/rate/usd/mad"
    assert rate.quote == "MAD"
    assert converted == 500


def test_api_422_reaches_the_service_as_invalid_currency():
    data = {"status": API_ERROR_CODE, "message": "invalid currency: XYZ"}
    session = FakeSession(response=FakeResponse(API_ERROR_CODE, data))
    with pytest.raises(InvalidCurrencyError, match="XYZ"):
        make_service(session).get_rate("USD", "XYZ")


def test_no_internet_reaches_the_service_as_unavailable():
    session = FakeSession(error=requests.ConnectionError())
    with pytest.raises(RateServiceUnavailableError):
        make_service(session).list_currencies()


def test_service_blocks_bad_input_before_calling_the_api():
    session = FakeSession(response=FakeResponse(HTTP_OK, {}))
    with pytest.raises(InvalidCurrencyError):
        make_service(session).get_rate("US", "EUR")
    assert session.last_url is None