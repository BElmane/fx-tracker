"""Unit tests for RateService, using a fake provider (no internet)."""

import pytest

from fx_tracker.errors import InvalidAmountError, InvalidCurrencyError
from fx_tracker.models import Currency, ExchangeRate
from fx_tracker.rate_provider import RateProvider
from fx_tracker.rate_service import RateService

FAKE_RATE = 0.5
FAKE_DATE = "2026-10-14"


class FakeRateProvider(RateProvider):
    """Pretends to be the API. Always gives the same answers."""

    def __init__(self):
        self.currency_calls = 0

    def get_currencies(self):
        self.currency_calls += 1
        return (Currency("USD", "US Dollar"), Currency("EUR", "Euro"))

    def get_rate(self, base, quote):
        return ExchangeRate(base, quote, FAKE_RATE, FAKE_DATE)


@pytest.fixture
def service():
    return RateService(FakeRateProvider())


def test_convert_returns_rate_and_amount(service):
    rate, converted = service.convert("USD", "EUR", 100)
    assert rate.rate == FAKE_RATE
    assert converted == 50


def test_codes_are_cleaned(service):
    rate = service.get_rate(" usd ", "eur")
    assert (rate.base, rate.quote) == ("USD", "EUR")


def test_same_currency_is_rejected(service):
    with pytest.raises(InvalidCurrencyError):
        service.get_rate("USD", "USD")


@pytest.mark.parametrize("bad_code", ["", "US", "USDD", "12A", None])
def test_bad_codes_are_rejected(service, bad_code):
    with pytest.raises(InvalidCurrencyError):
        service.get_rate(bad_code, "EUR")


@pytest.mark.parametrize("bad_amount", [0, -5])
def test_amount_must_be_positive(service, bad_amount):
    with pytest.raises(InvalidAmountError):
        service.convert("USD", "EUR", bad_amount)


def test_currencies_are_sorted_and_downloaded_once():
    provider = FakeRateProvider()
    service = RateService(provider)
    first = service.list_currencies()
    service.list_currencies()
    assert [currency.code for currency in first] == ["EUR", "USD"]
    assert provider.currency_calls == 1