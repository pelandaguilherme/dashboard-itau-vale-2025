# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Environment: Windows/PowerShell. Use the `python` command (Python 3.12), not `py`
— on this machine `py` resolves to Python 3.14, which does not yet have mature
wheel support for pandas/numpy/pyarrow used here.

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py          # runs at http://localhost:8501
```

There is no automated test suite (no pytest/unit tests). `data_loader.py`,
`metrics.py`, and `charts.py` are plain-Python modules with no Streamlit
dependency, so they can be exercised directly with `python -c "..."` imports
for quick verification without starting the Streamlit server — this is the
project's existing pattern for validating changes to data/metrics/chart logic.

## Architecture

Single-page Streamlit dashboard comparing ITUB4.SA (Itaú) and VALE3.SA (Vale)
stock performance for a fixed period (2025 by default). Five modules, each
with one responsibility:

- `config.py` — single source of truth for tickers, date range, per-ticker
  chart colors, and moving-average windows. `TICKER_COLORS` is threaded
  through every chart function in `charts.py` so a given ticker always
  renders in the same color across all panels.
- `data_loader.py` — Streamlit-independent data access. `fetch_ticker()`
  implements a three-tier fallback: try a live `yfinance.download()` — on
  failure or an empty result, fall back to the last on-disk CSV cache in
  `data/cache/` — if neither works, return an `"error"` status. It never
  raises; callers get back `(df, status, detail)` with `status` in
  `{"live", "cache", "error"}`. Note: `yfinance` sometimes returns a
  MultiIndex column header for single-ticker downloads — this is flattened
  immediately after the download call before caching.
- `metrics.py` — pure calculation functions operating on a `Close` price
  Series (cumulative return normalized to base 100, annualized volatility,
  drawdown, moving averages, and the summary table used in the UI).
- `charts.py` — pure functions that take already-computed data and return
  Plotly `go.Figure` objects; no Streamlit calls inside this module.
- `app.py` — the only module that imports Streamlit. It wraps
  `data_loader.fetch_all` in `st.cache_data(ttl=3600)` for in-session caching,
  and layers a manual `cache_bust` counter (stored in `st.session_state`) on
  top so the sidebar "Atualizar dados" button can force a fresh fetch by
  invalidating that cache — separate from the CSV fallback cache in
  `data_loader.py`, which persists across process restarts.

Data flow: `app.py` reads sidebar selections (tickers, date range, MA
windows) → calls the cached `fetch_all` → routes each ticker's `(df, status,
detail)` to an `st.error`/`st.warning` banner when not `"live"` → passes the
surviving `data` dict into `metrics.py` and `charts.py` to render cards,
charts, the summary table, and CSV downloads.

Adding a new ticker or changing the analysis period only requires editing
`config.py` (`TICKERS`, `TICKER_COLORS`, `START_DATE`/`END_DATE`) — no other
module hardcodes ticker symbols or dates.
