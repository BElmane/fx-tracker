# FX Tracker

FX Tracker is a Python app that shows live exchange rates between currencies. You pick two currencies, see the current rate, and convert an amount.

## Problem
Exchange rates change over time, which affects how much money a person receives when converting from one currency to another. It's hard to keep checking rates by hand and know when it's a good time to convert or send money.

## Users
- **People who send or receive money internationally**, like students whose families send money from another country to help with expenses.
- **Travelers** who want to know how much their money is worth before a trip, or what a price in another currency means in their own money.
- **Anyone who converts money between currencies** and wants to check the rate before making an exchange.

## Solution
A Python app where users pick supported currency pairs, see current exchange rates, and later track rate history and set a target rate to get notified when it's met.

## Technology
- Python 3.12
- [Frankfurter v2 API](https://frankfurter.dev/) for exchange rates (free, no API key)
- `requests` to call the API
- Streamlit for the user interface
- pytest for testing

## Features (Sprint 1)
- Pick "From" and "To" currencies from the supported list
- See the current exchange rate and the rate date
- Convert an amount
- Swap the two currencies with one click
- Friendly messages for bad input, no internet, or API errors (the app does not crash)

## Setup
You need Python 3.12 and Git.

```zsh
git clone https://github.com/BElmane/fx-tracker.git
cd fx-tracker
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the App
```zsh
streamlit run app.py
```
The app opens in your browser at `http://localhost:8501`. Press `Ctrl + C` in the terminal to stop it.

## Run the Tests
```zsh
pytest -v
```
There are 4 kinds of tests in the `tests` folder:
- `unit/`: one class at a time, using fake objects (no internet)
- `integration/`: the service and the API client working together (no internet)
- `regression/`: tricky cases that must keep working
- `acceptance/`: uses the real app like a user would (needs internet)

## Project Structure
```
fx-tracker/
├── app.py                    # Streamlit screen (UI only)
├── fx_tracker/
│   ├── config.py             # settings and constants
│   ├── errors.py             # custom errors
│   ├── models.py             # Currency and ExchangeRate data classes
│   ├── rate_provider.py      # abstract RateProvider (the contract)
│   ├── frankfurter_client.py # talks to the Frankfurter API
│   └── rate_service.py       # app rules (checks input, converts)
└── tests/
```

## Design Principles Used
- **Abstraction:** `RateProvider` is an abstract class that says what a rate source must do.
- **Inheritance and Polymorphism:** `FrankfurterClient` follows `RateProvider`, and so does the fake provider in the tests. The service can't tell them apart.
- **Encapsulation:** data classes are frozen, so they can't be changed, and private fields start with `_`.
- **Dependency Injection:** `RateService` gets its provider passed in, so it's easy to test and swap.
- **Single Responsibility:** the UI, the app rules, and the API code each live in their own file.
- **No magic numbers:** fixed values have names in `config.py`.

## Status
- **Sprint 1 (Weeks 5–9):** working prototype done. 35 tests passing.
- **Sprint 2 (Weeks 10–15):** planned: multi-pair tracking, rate history, target rates and alerts, a trend view, and design improvements.

## Project Links
- Canvas Individual Project page: https://nku.instructure.com/courses/91834/pages/individual-project-page-of-bebba-elmane
- Canvas Individual Project Progress page: https://nku.instructure.com/courses/91834/pages/individual-project-progress-page-of-bebba-elmane-in-ase420
- Sprint 1 Review presentation: presentation/sprint1_review.md
- User Manual (draft): docs/user_manual.md
- Architecture and Design Document (draft): docs/architecture.md
