---
marp: true
size: 4:3
paginate: true
---

# FX Tracker
### Know what your money is really worth

Bebba Elmane · ASE 420
https://github.com/BElmane/fx-tracker

---

## The Problem

- Exchange rates change every day
- $500 at 9.78 MAD = **4,890 MAD**
- $500 at 9.60 MAD = **4,800 MAD**
- Bad timing = **90 MAD lost**

**Users:** travelers, students whose families send money, anyone who converts money

---

## My Solution

A simple app that shows **live exchange rates**

- 165 currencies
- Real data from the Frankfurter API
- Convert any amount, swap in one click

---

## Demo

![w:600](images/app_rate.png)

---

## Demo: Errors

![w:600](images/app_warning.png)

Friendly warnings, and the app never crashes

---

## Weekly Progress Sprint 1

- **Week 5:** repo and README, tested the API by hand
- **Week 6:** chose Frankfurter v2 over v1
- **Week 7:** planned the app structure and tests
- **Week 8:** built the full prototype, 35 tests, PR #1 merged

---

## Sprint 1 Metrics

- Lines of code: **258** app, **324** tests
- Tests: **35** (21 unit, 4 integration, 5 regression, 5 acceptance)
- Features: **3 / 3**
- Requirements: **2 / 2**
- Burndown rate for features = **100%**
- Burndown rate for requirements = **100%**

---

## Design

- **Abstraction:** `RateProvider` is a contract for any data source
- **Dependency Injection:** `RateService` gets its provider passed in
- **Result:** tests use a fake provider, no internet needed
- **Refactoring:** moved shared test fakes into one file (`tests/fakes.py`)

---

## What Went Wrong

- Git workflow mistakes, like editing files in two places
- Small mistakes: unsaved files, indentation, a file-name typo
- Learning new tools while building(Streamlit, Apptest)

---

## What Went Well

- The design made testing easy
- All 4 test types done
- The prototype works with real rates

---

## Improvement Plan

- Small commits every week
- Run tests before every commit

---

## Sprint 2 Goals

- Track many currency pairs
- Save rate history and show a trend chart
- Set a target rate and get an alert
- User Manual, Architecture Doc, GitHub Pages

**Planned:** 5 features, 3 requirements, tests for all 4 types

---

## Sprint 2 Timeline

- **Week 9:** S1P
- **Weeks 10–11:** refactor Sprint 1 code
- **Weeks 12–13:** multi-pair tracking, target rates, docs, website
- **Week 14:** trend view and testing
- **Week 15:** final submission (12/5)

---

# Questions?

https://github.com/BElmane/fx-tracker