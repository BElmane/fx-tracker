"""FX Tracker screen (Streamlit). This file only shows things. The rules live in RateService."""

import streamlit as st

from fx_tracker.config import DEFAULT_FROM_CURRENCY, DEFAULT_TO_CURRENCY
from fx_tracker.errors import FxTrackerError, InvalidAmountError, InvalidCurrencyError
from fx_tracker.frankfurter_client import FrankfurterClient
from fx_tracker.rate_service import RateService

DEFAULT_AMOUNT = 100.0
AMOUNT_STEP = 10.0
RATE_DECIMALS = 4
MONEY_DECIMALS = 2


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


main()
