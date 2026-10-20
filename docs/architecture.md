---
marp: true
size: 4:3
paginate: true
---

# FX Tracker
## Architecture and Design Document (Draft)

Bebba Elmane · ASE 420 · Fall 2026

---

## Overview

FX Tracker is a Python app with 3 layers:

| Layer | File | Job |
|---|---|---|
| Screen | `app.py` | Shows things to the user (Streamlit) |
| Rules | `fx_tracker/rate_service.py` | Checks input and converts money |
| Data | `fx_tracker/frankfurter_client.py` | Gets rates from the Frankfurter v2 API |

Each layer only talks to the one below it.

---

## Main Classes

| Class | File | Responsibility |
|---|---|---|
| `RateProvider` | `rate_provider.py` | Abstract contract: `get_currencies()` and `get_rate()` |
| `FrankfurterClient` | `frankfurter_client.py` | Follows `RateProvider`, calls the API, turns HTTP errors into our errors |
| `RateService` | `rate_service.py` | Cleans and checks codes, blocks same-currency pairs, converts amounts |
| `Currency`, `ExchangeRate` | `models.py` | Frozen data classes |
| `FxTrackerError` and children | `errors.py` | Our own error types |

---

## How a Rate Request Works

1. The user picks USD → EUR and types 500 in `app.py`.
2. `app.py` calls `RateService.convert("USD", "EUR", 500)`.
3. `RateService` cleans the codes and checks the amount.
4. `RateService` calls `provider.get_rate("USD", "EUR")`.
5. `FrankfurterClient` sends `GET /v2/rate/usd/eur`.
6. The JSON comes back as an `ExchangeRate` object.
7. `RateService` returns the rate and the converted amount.
8. `app.py` shows the result card.

---

## How Errors Work

| Problem | Error raised | What the user sees |
|---|---|---|
| Bad code, same currency, HTTP 400/404/422 | `InvalidCurrencyError` | Yellow warning |
| Amount 0 or less | `InvalidAmountError` | Yellow warning |
| No internet, timeout, server error, bad JSON | `RateServiceUnavailableError` | Red message |

All errors inherit from `FxTrackerError`, so the screen can catch them in one place. The app never crashes.

---

## Design Principles

| Principle | Where it is used |
|---|---|
| Abstraction | `RateProvider` hides how rates are fetched |
| Inheritance / Polymorphism | `FrankfurterClient` and the test fake both follow `RateProvider` |
| Encapsulation | Frozen data classes, private `_fields` |
| Dependency Injection | `RateService(provider)`, `FrankfurterClient(session)` |
| Dependency Inversion | `RateService` depends on the abstract contract, not the API |
| Single Responsibility | Screen, rules, and data in separate files |
| No magic numbers | Constants in `config.py` and named constants in each file |

---

## Testing Strategy

| Type | Folder | What it checks |
|---|---|---|
| Unit | `tests/unit/` | One class at a time, with fakes |
| Integration | `tests/integration/` | Service + client together, fake internet |
| Regression | `tests/regression/` | Tricky cases that must keep working |
| Acceptance | `tests/acceptance/` | The real app, used like a user (Streamlit AppTest) |

Shared fakes live in `tests/fakes.py`.

---

## Key Decisions

- **Frankfurter v2 over v1:** v2 has a simple single-pair endpoint and clear error codes.
- **Streamlit for the UI:** all Python, quick to build, and looks clean on a projector.
- **Python 3.12:** some packages don't support 3.14 yet.
- **Fakes instead of the real API in most tests:** tests are fast, offline, and give the same result every time.

---

## Planned for Sprint 2

- A storage class for rate history, passed in with DI
- A history and trend view
- Target rates and alerts, using a design pattern that fits
- A full version of this document, with a UML class diagram and a PDF export