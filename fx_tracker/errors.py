"""Custom errors for FX Tracker."""


class FxTrackerError(Exception):
    """Parent class for every FX Tracker error."""


class InvalidCurrencyError(FxTrackerError):
    """The currency code is not supported (API returns HTTP 422)."""


class RateServiceUnavailableError(FxTrackerError):
    """The API could not be reached (no internet, timeout, or server error)."""


class InvalidAmountError(FxTrackerError):
    """The amount to convert must be greater than 0."""