"""Unit tests for the data models."""

from dataclasses import FrozenInstanceError

import pytest

from fx_tracker.models import ExchangeRate


def test_convert_multiplies_amount_by_rate():
    rate = ExchangeRate("USD", "EUR", 0.5, "2026-10-14")
    assert rate.convert(100) == 50


def test_exchange_rate_cannot_be_changed():
    rate = ExchangeRate("USD", "EUR", 0.5, "2026-10-14")
    with pytest.raises(FrozenInstanceError):
        rate.rate = 2
        