"""FX Tracker screen (Streamlit). This file only shows things. The rules live in RateService."""

import pandas as pd
import streamlit as st

from fx_tracker.config import (
    DEFAULT_FROM_CURRENCY,
    DEFAULT_HISTORY_DAYS,
    DEFAULT_TO_CURRENCY,
    HISTORY_DAY_OPTIONS,
)
from fx_tracker.errors import FxTrackerError, InvalidAmountError, InvalidCurrencyError
from fx_tracker.frankfurter_client import FrankfurterClient
from fx_tracker.rate_service import RateService

DEFAULT_AMOUNT = 100.0
AMOUNT_STEP = 10.0
RATE_DECIMALS = 4
MONEY_DECIMALS = 2
HISTORY_LABELS = {7: "1 week", 30: "1 month", 90: "3 months"}
CHART_COLOR = "#E8772E"


@st.cache_resource
def build_service() -> RateService:
    """Create the service once and inject the real API client."""
    return RateService(FrankfurterClient())


def swap_currencies():
    """Switch the From and To currencies."""
    st.session_state.from_code, st.session_state.to_code = (
        st.session_state.to_code,
        st.session_state.from_code,
    )


def show_history(service: RateService, base: str, quote: str):
    """Draw a trend chart of the rate for the period the user picks."""
    st.subheader("Trend")
    days = st.radio(
        "Period",
        HISTORY_DAY_OPTIONS,
        index=HISTORY_DAY_OPTIONS.index(DEFAULT_HISTORY_DAYS),
        format_func=HISTORY_LABELS.get,
        horizontal=True,
        key="history_days",
    )

    try:
        history = service.get_history(base, quote, days)
    except FxTrackerError as error:
        st.warning(f"Can't show the trend right now. {error}")
        return

    if not history:
        st.info("No history found for this pair.")
        return

    chart_data = pd.DataFrame(
        {
            "Date": pd.to_datetime([rate.date for rate in history]),
            f"1 {base} in {quote}": [rate.rate for rate in history],
        }
    ).set_index("Date")
    st.line_chart(chart_data, color=CHART_COLOR)

    first, last = history[0], history[-1]
    st.caption(
        f"From {first.rate:.{RATE_DECIMALS}f} on {first.date} "
        f"to {last.rate:.{RATE_DECIMALS}f} on {last.date}"
    )


def main():
    st.set_page_config(page_title="FX Tracker", page_icon="💱")
    st.title("💱 FX Tracker")
    st.caption("Live exchange rates for supported currencies")

    service = build_service()
    try:
        currencies = service.list_currencies()
    except FxTrackerError as error:
        st.error(f"{error} Check your internet and refresh the page.")
        st.stop()

    names = {currency.code: currency.name for currency in currencies}
    codes = tuple(names)

    st.session_state.setdefault("from_code", DEFAULT_FROM_CURRENCY)
    st.session_state.setdefault("to_code", DEFAULT_TO_CURRENCY)

    def label(code):
        return f"{code} · {names[code]}"

    left, middle, right = st.columns([5, 1, 5], vertical_alignment="bottom")
    with left:
        st.selectbox("From", codes, key="from_code", format_func=label)
    with middle:
        st.button("⇄", on_click=swap_currencies, help="Swap currencies")
    with right:
        st.selectbox("To", codes, key="to_code", format_func=label)

    amount = st.number_input("Amount", min_value=0.0, value=DEFAULT_AMOUNT, step=AMOUNT_STEP)

    try:
        rate, converted = service.convert(
            st.session_state.from_code, st.session_state.to_code, amount
        )
    except (InvalidCurrencyError, InvalidAmountError) as error:
        st.warning(str(error))
        return
    except FxTrackerError as error:
        st.error(f"{error} Check your internet and try again.")
        return

    with st.container(border=True):
        st.metric(label=f"1 {rate.base} =", value=f"{rate.rate:.{RATE_DECIMALS}f} {rate.quote}")
        st.success(
            f"{amount:,.{MONEY_DECIMALS}f} {rate.base} = {converted:,.{MONEY_DECIMALS}f} {rate.quote}"
        )
        st.caption(f"Rate date: {rate.date} · Source: Frankfurter")

    show_history(service, rate.base, rate.quote)


main()