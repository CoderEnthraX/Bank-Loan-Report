# Sniper accuracy research (asked 2026-11-22) - progress / checkpoint
Goal: raise the VWAP Orderflow Sniper's accuracy on gold M5 / M15 (also H1 / H2 / H3); settings, combinations, new order flow concepts; Excel.
Protocol: signals by the research engine (= the EA / Pine logic, validated); outcome on M1 from the minute after the signal bar, stop first,
costs 0.23 / oz (spread 0.16 + $7 a lot); accuracy = % reaching X R before the stop; train 2021-2023, test 2024 - 2 Oct 2026.
## Steps
- [ ] 1 data.py: TF bars, intrabar delta, VWAP, filters -> cache_<tf>.npz
- [ ] 2 engine.py: numba Sniper kernel; parity with the EA (sim run q3 2026: 149 signals)
- [ ] 3 outcome kernel + baseline per TF
- [ ] 4 one-at-a-time sweeps of the Sniper settings
- [ ] 5 new order flow concepts
- [ ] 6 combined search (train) -> test
- [ ] 7 Excel + docs
- [x] 1 data.py (5 caches, m1.npz); VWAP = the EA's on 24,409 bars (diff <= 5e-9)
- [x] 2 engine.py = the EA: 148 / 148 signals (q3 2026), also after the research extensions (ctx 1 band reversal, ctx 2 levels pd / sx / pw, vside, filter slots mode 1-5)
- [x] 3 outcome.py, evalx.py; baseline: accuracy = random-entry level (1 / (1 + X)): M5 82.9 / 66.5 / 50.3 % at 0.2 / 0.5 / 1R, net -0.09..-0.10R; M15 similar; H1 8 signals (ratio 2.2 too strict with 60 M1 intrabars)
- [x] 4 sweep1_<tf>.txt: no single setting gives a robust edge (best: minZoneN 2, volLen 80, absSens 1.0: +1..3 pts)
- [ ] 5/6 search.py: random search, select on min(edge 2021-22, edge 2023), test 2024-26
- [x] search: 16,755 (M5) / 9,349 (M15) / ~5,000 each (H1-H3) eligible configs; selection on 2021-23 -> test 2024-26:
      M5 1R top10 +2.6 pts (all +0.85); M15 ~0 (all +1.25); H1 +5.3 (all +1.8); H2 +4.1 (all +2.3); H3 +10.7 (all +3.9)
- [x] ml.py (LightGBM, all features): test AUC 0.50 (M5, M15, H1, H2), 0.52 (H3) -> the features carry ~no information
- [ ] refine.py (run_refine.sh) -> final picks (train-only rule) -> detail -> concepts -> workbook
