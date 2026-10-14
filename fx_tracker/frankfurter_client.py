"""Talks to the Frankfurter v2 exchange-rate API."""

import requests

from fx_tracker.config import API_BASE_URL, REQUEST_TIMEOUT_SECONDS
from fx_tracker.errors import InvalidCurrencyError, RateServiceUnavailableError
from fx_tracker.models import Currency, ExchangeRate
from fx_tracker.rate_provider import RateProvider

# HTTP codes the API uses when the currency or request is bad.
INVALID_REQUEST_CODES = (400, 404, 422)


class FrankfurterClient(RateProvider):
    """Gets currencies and rates from Frankfurter."""

    def __init__(self, session=None, base_url=API_BASE_URL, timeout=REQUEST_TIMEOUT_SECONDS):
        self._session = session or requests.Session()
        self._base_url = base_url
        self._timeout = timeout

    def get_currencies(self) -> tuple[Currency, ...]:
        data = self._get_json("/currencies")
        return tuple(
            Currency(code=item["iso_code"], name=item["name"], symbol=item.get("symbol", ""))
            for item in data
        )

    def get_rate(self, base: str, quote: str) -> ExchangeRate:
        data = self._get_json(f"/rate/{base.lower()}/{quote.lower()}")
        return ExchangeRate(
            base=data["base"],
            quote=data["quote"],
            rate=float(data["rate"]),
            date=data["date"],
        )

    def _get_json(self, path: str):
        """Send a GET request and return the JSON, or raise our own errors."""
        url = f"{self._base_url}{path}"
        try:
            response = self._session.get(url, timeout=self._timeout)
        except requests.RequestException as error:
            raise RateServiceUnavailableError("Can't reach the rate service.") from error

        if response.status_code in INVALID_REQUEST_CODES:
            raise InvalidCurrencyError(self._error_message(response))
        if not response.ok:
            raise RateServiceUnavailableError(
                f"Rate service error (HTTP {response.status_code})."
            )

        try:
            return response.json()
        except ValueError as error:
            raise RateServiceUnavailableError("Rate service sent bad data.") from error

    @staticmethod
    def _error_message(response) -> str:
        """Get the API's error message, or a simple default."""
        try:
            return response.json().get("message", "Invalid currency.")
        except ValueError:
            return "Invalid currency."
        