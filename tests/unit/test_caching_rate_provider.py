"""Unit tests for the CachingRateProvider proxy."""

import pytest

from fx_tracker.caching_rate_provider import CachingRateProvider
from fx_tracker.errors import InvalidCurrencyError
from fx_tracker.rate_provider import RateProvider
from tests.fakes import UNSUPPORTED_CODE, FakeRateProvider

MAX_AGE_SECONDS = 300


class CountingProvider(FakeRateProvider):
    """A fake provider that counts how many times get_rate is called."""

    def __init__(self):
        super().__init__()
        self.rate_calls = 0

    def get_rate(self, base, quote):
        self.rate_calls += 1
        return super().get_rate(base, quote)


class FakeClock:
    """A clock we can move forward by hand."""

    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


def make_proxy():
    real = CountingProvider()
    clock = FakeClock()
    proxy = CachingRateProvider(real, max_age_seconds=MAX_AGE_SECONDS, clock=clock)
    return proxy, real, clock


def test_same_pair_twice_calls_the_real_provider_once():
    proxy, real, _ = make_proxy()
    proxy.get_rate("USD", "MAD")
    proxy.get_rate("USD", "MAD")
    assert real.rate_calls == 1


def test_different_pairs_are_saved_separately():
    proxy, real, _ = make_proxy()
    proxy.get_rate("USD", "MAD")
    proxy.get_rate("EUR", "USD")
    assert real.rate_calls == 2


def test_old_rates_are_fetched_again():
    proxy, real, clock = make_proxy()
    proxy.get_rate("USD", "MAD")
    clock.now += MAX_AGE_SECONDS + 1
    proxy.get_rate("USD", "MAD")
    assert real.rate_calls == 2


def test_errors_are_not_saved():
    proxy, real, _ = make_proxy()
    for _ in range(2):
        with pytest.raises(InvalidCurrencyError):
            proxy.get_rate("USD", UNSUPPORTED_CODE)
    assert real.rate_calls == 2


def test_currencies_are_fetched_only_once():
    proxy, real, _ = make_proxy()
    proxy.get_currencies()
    proxy.get_currencies()
    assert real.currency_calls == 1


def test_history_passes_straight_through():
    proxy, real, _ = make_proxy()
    history = proxy.get_history("USD", "MAD", None)
    assert len(history) == 2
    assert real.last_history_pair == ("USD", "MAD")


def test_proxy_follows_the_same_contract():
    proxy, _, _ = make_proxy()
    assert isinstance(proxy, RateProvider)