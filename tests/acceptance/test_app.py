"""Acceptance tests: use the real app like a user would.
These call the real Frankfurter API, so they need internet."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP_FILE = str(Path(__file__).resolve().parents[2] / "app.py")
TIMEOUT_SECONDS = 30


@pytest.fixture(autouse=True)
def use_a_temporary_folder(tmp_path, monkeypatch):
    """Run every test in an empty folder, so the real watchlist.json is never touched."""
    monkeypatch.chdir(tmp_path)


def run_app():
    app = AppTest.from_file(APP_FILE, default_timeout=TIMEOUT_SECONDS)
    app.run()
    return app


def click_button(app, label):
    """Find a button by its label, click it, and let the app refresh."""
    button = next(button for button in app.button if button.label == label)
    button.click().run()


def add_to_watchlist(app, base, quote, target=0.0):
    """Fill in the Watchlist form like a user, then click Add."""
    app.selectbox(key="watch_from").set_value(base)
    app.selectbox(key="watch_to").set_value(quote)
    app.number_input(key="watch_target").set_value(target)
    click_button(app, "Add to watchlist")


def test_user_sees_a_rate_when_the_app_opens():
    app = run_app()
    assert not app.exception
    assert "EUR" in app.metric[0].value


def test_user_can_swap_currencies():
    app = run_app()
    app.button[0].click().run()
    assert app.selectbox(key="from_code").value == "EUR"
    assert app.selectbox(key="to_code").value == "USD"


def test_user_can_pick_another_currency():
    app = run_app()
    app.selectbox(key="to_code").set_value("MAD").run()
    assert "MAD" in app.metric[0].value


def test_zero_amount_shows_a_friendly_warning():
    app = run_app()
    app.number_input[0].set_value(0).run()
    assert app.warning[0].value == "Enter an amount greater than 0."


def test_same_currency_shows_a_friendly_warning():
    app = run_app()
    app.selectbox(key="to_code").set_value("USD").run()
    assert app.warning[0].value == "Pick two different currencies."


def test_new_user_sees_an_empty_watchlist():
    app = run_app()
    assert any("Your watchlist is empty" in info.value for info in app.info)


def test_user_can_add_a_pair_to_the_watchlist():
    app = run_app()
    add_to_watchlist(app, "USD", "MAD")
    assert "USD/MAD" in app.dataframe[0].value["Pair"].tolist()


def test_user_sees_an_alert_when_the_target_is_reached():
    app = run_app()
    add_to_watchlist(app, "EUR", "USD", 0.5)
    assert any("Target reached: EUR/USD" in message.value for message in app.success)


def test_adding_the_same_pair_twice_shows_a_warning():
    app = run_app()
    add_to_watchlist(app, "USD", "MAD")
    add_to_watchlist(app, "USD", "MAD")
    assert any("already in your watchlist" in warning.value for warning in app.warning)