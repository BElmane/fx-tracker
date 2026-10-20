---
marp: true
size: 4:3
paginate: true
---

# FX Tracker
## User Manual (Draft)

Bebba Elmane · ASE 420 

---

## What FX Tracker Does

FX Tracker shows the live exchange rate between two currencies and converts an amount for you.

- 165 supported currencies
- Real rates from the Frankfurter API
- No account or sign-up needed

---

## What You Need

- A Mac, Windows, or Linux computer
- Python 3.12
- Git
- An internet connection (to get live rates)

---

## Install

```zsh
git clone https://github.com/BElmane/fx-tracker.git
cd fx-tracker
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows, use `.venv\Scripts\activate` instead of `source .venv/bin/activate`.

---

## Start the App

```zsh
streamlit run app.py
```

The app opens in your browser at `http://localhost:8501`.

To stop it, click the terminal and press `Ctrl + C`.

---

## Check a Rate

1. Pick a currency in **From** (for example, USD).
2. Pick a currency in **To** (for example, MAD).
3. Type an **Amount** (for example, 500).
4. The result card shows the rate, the converted amount, and the rate date.

Click the **swap button** between the two boxes to switch From and To.

---

## Messages You Might See

| Message | What it means | What to do |
|---|---|---|
| Pick two different currencies. | From and To are the same | Change one of them |
| Enter an amount greater than 0. | The amount is 0 | Type a bigger number |
| Can't reach the rate service. | No internet, or the API is down | Check your internet and try again |
| Invalid currency | The API does not support that code | Pick another currency |

---

## Run the Tests (for developers)

```zsh
pytest -v
```

The acceptance tests use the real API, so they need internet. All other tests run offline.

---

## Troubleshooting

- **SSL certificate error on Mac:** run the "Install Certificates" file in your Python folder (Applications → Python 3.12).
- **Port 8501 is already in use:** another copy of the app is running. Close it, or run `streamlit run app.py --server.port 8502`.
- **`ModuleNotFoundError`:** the venv is not on. Run `source .venv/bin/activate` again.

---

## Coming in Sprint 2

- Track several currency pairs at once
- See rate history and a trend chart
- Set a target rate and get an alert when it's reached