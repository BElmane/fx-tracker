"""FX Tracker screen (Streamlit). This file only shows things. The rules live in the services."""

import altair as alt
import pandas as pd
import streamlit as st

from fx_tracker.alert_rules import ABOVE, ALERT_RULES, BELOW
from fx_tracker.config import (
    DEFAULT_FROM_CURRENCY,
    DEFAULT_HISTORY_DAYS,
    DEFAULT_TO_CURRENCY,
    HISTORY_DAY_OPTIONS,
)
from fx_tracker.errors import FxTrackerError, InvalidAmountError, InvalidCurrencyError
from fx_tracker.frankfurter_client import FrankfurterClient
from fx_tracker.rate_service import RateService
from fx_tracker.watchlist_service import WatchlistService
from fx_tracker.watchlist_store import JsonWatchlistStore

DEFAULT_AMOUNT = 100.0
AMOUNT_STEP = 10.0
RATE_DECIMALS = 4
MONEY_DECIMALS = 2
HISTORY_LABELS = {7: "1 week", 30: "1 month", 90: "3 months"}
CHART_COLOR = "#E8772E"
NO_TARGET = 0.0
TARGET_STEP = 0.01
DIRECTION_LABELS = {ABOVE: "Goes up to", BELOW: "Goes down to"}


@st.cache_resource
def build_service() -> RateService:
    """Create the rate service once and inject the real API client."""
    return RateService(FrankfurterClient())


@st.cache_resource
def build_watchlist() -> WatchlistService:
    """Create the watchlist service once and inject the real file store."""
    return WatchlistService(JsonWatchlistStore(), build_service())


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
            "Rate": [rate.rate for rate in history],
        }
    )
    chart = (
        alt.Chart(chart_data)
        .mark_line(color=CHART_COLOR)
        .encode(
            x=alt.X("Date:T", title=None),
            y=alt.Y("Rate:Q", title=f"1 {base} in {quote}", scale=alt.Scale(zero=False)),
            tooltip=["Date:T", "Rate:Q"],
        )
    )
    st.altair_chart(chart)

    first, last = history[0], history[-1]
    st.caption(
        f"From {first.rate:.{RATE_DECIMALS}f} on {first.date} "
        f"to {last.rate:.{RATE_DECIMALS}f} on {last.date}"
    )


def show_converter(service: RateService, codes: tuple[str, ...], label):
    """The Convert tab: pick two currencies, see the rate, convert, and see the trend."""
    st.session_state.setdefault("from_code", DEFAULT_FROM_CURRENCY)
    st.session_state.setdefault("to_code", DEFAULT_TO_CURRENCY)

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
        st.metric(
            label="Current rate",
            value=f"1 {rate.base} = {rate.rate:.{RATE_DECIMALS}f} {rate.quote}",
        )
        st.success(
            f"{amount:,.{MONEY_DECIMALS}f} {rate.base} = {converted:,.{MONEY_DECIMALS}f} {rate.quote}"
        )
        st.caption(f"Rate date: {rate.date} · Source: Frankfurter")

    show_history(service, rate.base, rate.quote)


def show_watchlist(
    watchlist: WatchlistService, service: RateService, codes: tuple[str, ...], label
):
    """The Watchlist tab: alerts, add a pair, see your pairs, and remove a pair."""
    alerts_box = st.container()

    st.subheader("Add a pair")
    with st.form("add_pair", clear_on_submit=True):
        left, right = st.columns(2)
        with left:
            base = st.selectbox(
                "From",
                codes,
                index=codes.index(DEFAULT_FROM_CURRENCY),
                format_func=label,
                key="watch_from",
            )
        with right:
            quote = st.selectbox(
                "To",
                codes,
                index=codes.index(DEFAULT_TO_CURRENCY),
                format_func=label,
                key="watch_to",
            )
        target = st.number_input(
            "Target rate (leave 0 for no target)",
            min_value=NO_TARGET,
            value=NO_TARGET,
            step=TARGET_STEP,
            format="%.4f",
            key="watch_target",
        )
        direction = st.radio(
            "Alert me when the rate",
            tuple(DIRECTION_LABELS),
            format_func=DIRECTION_LABELS.get,
            horizontal=True,
            key="watch_direction",
        )
        submitted = st.form_submit_button("Add to watchlist")

    if submitted:
        try:
            item = watchlist.add(base, quote, target or None, direction)
            st.success(f"Added {item.pair}.")
        except FxTrackerError as error:
            st.warning(str(error))

    st.subheader("Your watchlist")
    try:
        items = watchlist.items()
    except FxTrackerError as error:
        st.error(str(error))
        return

    if not items:
        st.info("Your watchlist is empty. Add a pair above.")
        return

    rows = []
    for item in items:
        try:
            current = f"{service.get_rate(item.base, item.quote).rate:.{RATE_DECIMALS}f}"
        except FxTrackerError:
            current = "Not available"
        if item.target is None:
            target_text = "No target"
        else:
            target_text = f"{DIRECTION_LABELS[item.direction]} {item.target:.{RATE_DECIMALS}f}"
        rows.append({"Pair": item.pair, "Current rate": current, "Target": target_text})
    st.dataframe(pd.DataFrame(rows), hide_index=True)

    left, right = st.columns([3, 1], vertical_alignment="bottom")
    with left:
        to_remove = st.selectbox("Remove a pair", [item.pair for item in items], key="remove_pair")
    with right:
        if st.button("Remove", key="remove_button"):
            watchlist.remove(to_remove)
            st.rerun()

    with alerts_box:
        try:
            alerts = watchlist.check_alerts()
        except FxTrackerError as error:
            st.warning(f"Can't check your alerts right now. {error}")
            return
        for alert in alerts:
            rule = ALERT_RULES[alert.item.direction]
            st.success(
                f"Target reached: {alert.item.pair} {rule.label} "
                f"{alert.item.target:.{RATE_DECIMALS}f}. It's now {alert.rate.rate:.{RATE_DECIMALS}f}."
            )


def main():
    st.set_page_config(page_title="FX Tracker", page_icon="💱")
    st.title("💱 FX Tracker")
    st.caption("Live exchange rates for supported currencies")

    service = build_service()
    watchlist = build_watchlist()
    try:
        currencies = service.list_currencies()
    except FxTrackerError as error:
        st.error(f"{error} Check your internet and refresh the page.")
        st.stop()

    names = {currency.code: currency.name for currency in currencies}
    codes = tuple(names)

    def label(code):
        return f"{code} · {names[code]}"

    convert_tab, watchlist_tab = st.tabs(["Convert", "Watchlist"])
    with convert_tab:
        show_converter(service, codes, label)
    with watchlist_tab:
        show_watchlist(watchlist, service, codes, label)


main()