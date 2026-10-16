"""Acceptance tests: use the real app like a user would.
These call the real Frankfurter API, so they need internet."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

APP_FILE = str(Path(__file__).resolve().parents[2] / "app.py")
TIMEOUT_SECONDS = 30


def run_app():
    app = AppTest.from_file(APP_FILE, default_timeout=TIMEOUT_SECONDS)
    app.run()
    return app


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
    