# Entry research kit (gold, FxPro, 4 Jan 2021 - 2 Oct 2026)

Goal of the project: find an ENTRY rule (new or a change to the Auction Retest indicator) that raises the hit rate of every target
TP1-TP4 (0.6 / 1 / 1.5 / 2 R, R = stop distance) with a REAL edge that holds out of sample. The rule must be decidable at a bar's
close from data known then (so it can be coded in Pine and MQL5): OHLC, tick volume, spread, session VWAP / sigma, week / month VWAP,
ATR, time (UTC / New York / London local time), earlier bars of the same or a higher timeframe.

## Data and code (all in `entry/`, Python: `python3 -I script.py`, put `sys.path.insert(0, '<scratchpad>/entry')` first)
- `data.load(tf)` tf in M1 / M5 / M15 / H1 -> dict of numpy arrays: `O H L C TV SP` (SP = spread in price), `utc` (bar open, epoch s),
  `atr` (RMA 14), `V SD` session VWAP and its sigma (reset at each server day = the indicator's session), `Vw SDw`, `Vm SDm` (week /
  month VWAP), `ds` (session start), `vb` (bars since session start), `ist_min`, `utc_min`, `utc_wd`, `year`, `month`, `n`.
- `kit.local_min(tf, 'ny' | 'london')` -> local minutes after midnight (DST aware) per bar.
- `signals.raw(tf)` -> every raw signal of the indicator (dict: `i`, `d`, `entry` = its retest limit, `stop_h` = its stop, `sigH`, `sigL`).
- `kit.evaluate(tf, i, d, entry, stop, mode, window, name)` -> simulates every entry on its own (no one-trade-at-a-time), prints and
  returns train / valid stats: n, per month, fill rate, hit% TP1-TP4, EXCESS edge per TP and averaged, E at TP1 / TP4 after spread.
  mode 0 limit (touch within `window` bars), 1 market (entry must be `C[i]`; filled next bar), 2 stop entry (trade through `entry`).
- `kit.outcomes_of(...)` -> raw outcome arrays (`mfe_m` = max favourable excursion in R before the stop on the 1-minute path; hit TPk
  if `mfe_m >= TPk`), `fill_bar`, `exit_m` ...
- `features.build(tf, s)` -> ~60 causal features for given signals; `ev.py`, `dataset.py` (ds_TF.pkl = the indicator's signals with
  features and outcomes), `bars_TF.pkl` (every bar, long and short market entries, stop 1.8 ATR).

## Protocol (must follow)
- Splits: train 2021-01..2023-12, valid 2024-01..2025-06, TEST 2025-07..2026-10. NEVER look at TEST (kit excludes it by default).
- Judge on EXCESS edge = hit% minus random entries of the same direction in the same period. Gold rose ~60% in 2024-25, so longs
  look good in valid whatever the rule; the excess removes that. A rule is interesting only if its average excess edge is positive in
  BOTH train and valid, for longs AND shorts separately (or it is a one-direction rule that you justify), with enough trades
  (M5 >= 20 a month, M15 >= 8 a month, H1 >= 3 a month) and preferably on more than one timeframe.
- Standard error of a hit rate ~ 50 / sqrt(n) points: with n = 1,000 an excess of +1.6 is one standard error. Many rules are tried, so
  treat anything under ~3 standard errors in train as noise unless valid confirms it with the same sign and similar size.
- Prefer few, simple, explainable conditions. Report what failed too (briefly).

## What is already known (do not repeat)
- Random entries: TP1-TP4 hit about 62 / 50 / 40 / 33 % (= no-edge rates 1/(1+R)). The indicator's signals are the same: excess ~0
  (M5 -1.0 train / 0.0 valid; M15 -0.5 / -2.3; H1 about -3). Spread costs 0.07 R a trade on M5 at 1.8 ATR (0.17 R on M1).
- LightGBM on ~60 features cannot rank the indicator's signals (valid AUC 0.50-0.51). On every M15 bar AUC 0.53, mostly daily trend
  features (regime). Single features on the signals: +-1-3 pts, not stable.
- Retest limit = adverse selection: signals whose limit fills would have lost at market (TP1 ~50%); those that never fill would have
  won (TP1 ~95%). Market entry on all signals = random. Stop entry at the signal bar's extreme +0.05 ATR = +0.5 excess (noise).
- Time of day (New York local time, drift-neutral, every bar): shorts favoured NY 07:00-10:00 (D about -2 to -4 pts), longs favoured
  NY 14:00-17:00 (+3 to +5 pts, every year), NY 18:00 reopen slightly long. Small but consistent.

## Order flow (added 2026-11-08, `of.py`): tick volume only
Gold CFD data (FxPro, OANDA) has TICK volume, no bid/ask (aggressor) volume, so real delta / footprint is impossible; TradingView's
order-flow tools on XAUUSD estimate from tick volume too. `of.py` gives what can be computed (all causal, at a bar's close):
- `of.flow(tf)` per chart bar: `vol` (tick volume), `dtk` / `dcl` = estimated delta (sum over the bar's 1-minute candles of
  TV x sign(C-O), or TV x (2C-H-L)/(H-L)), `cvd_tk` / `cvd_cl` = session cumulative delta (reset at the session start = the VWAP's),
  `dpoc dvah dval` developing volume profile (POC, 70 % value area) at the bar's close, `ppoc pvah pval` the previous session's.
- Profile = every 1-minute candle's tick volume spread evenly over its high-low range in $0.50 bins, per session (server day).
- `of.rvp(tf, i, prices, 'dev'|'prior')` = relative volume at a price (bin volume / mean of the traded bins): LVN ~ < 0.5, HVN ~ > 1.5.
  At breakouts the developing profile is thin (price is new), so RVP at the signal close is low (median 0.19 on M15): compare with care.
- `of.path_rvp(tf, i, p0, p1, which)` -> (min, max, mean) RVP over the bins between two prices (e.g. entry -> TP1 / entry -> stop).
- `of.store(tf)` -> per-session final histograms (base, nb, off, flat; bin k price = (base + k + 0.5) x 0.5) for composite profiles.
