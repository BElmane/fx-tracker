"""Strategy pattern: different ways to decide if a target rate has been reached."""

from abc import ABC, abstractmethod

ABOVE = "above"
BELOW = "below"
DEFAULT_DIRECTION = ABOVE


class AlertRule(ABC):
    """The contract for every alert rule."""

    label = ""

    @abstractmethod
    def is_met(self, current: float, target: float) -> bool:
        """Return True if the current rate reached the target."""


class AtOrAboveRule(AlertRule):
    """Alert when the rate goes up to the target or higher."""

    label = "went up to"

    def is_met(self, current: float, target: float) -> bool:
        return current >= target


class AtOrBelowRule(AlertRule):
    """Alert when the rate goes down to the target or lower."""

    label = "went down to"

    def is_met(self, current: float, target: float) -> bool:
        return current <= target


ALERT_RULES = {ABOVE: AtOrAboveRule(), BELOW: AtOrBelowRule()}