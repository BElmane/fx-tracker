"""Unit tests for the alert rule strategies."""

import pytest

from fx_tracker.alert_rules import ALERT_RULES, AtOrAboveRule, AtOrBelowRule


@pytest.mark.parametrize(
    ("current", "target", "expected"),
    [(10.5, 10.0, True), (10.0, 10.0, True), (9.9, 10.0, False)],
)
def test_above_rule(current, target, expected):
    assert AtOrAboveRule().is_met(current, target) is expected


@pytest.mark.parametrize(
    ("current", "target", "expected"),
    [(9.5, 10.0, True), (10.0, 10.0, True), (10.1, 10.0, False)],
)
def test_below_rule(current, target, expected):
    assert AtOrBelowRule().is_met(current, target) is expected


def test_rules_are_picked_by_name():
    assert isinstance(ALERT_RULES["above"], AtOrAboveRule)
    assert isinstance(ALERT_RULES["below"], AtOrBelowRule)