# Spec: BE trigger and salvage trigger exits (Auction Retest research engine)

Engine under test: `bese/ref_gbe.py` (`run(tf, opts)` returns trades). Data: `gold/geng.py` `prepare(tf, vw, src)` returns arrays
`O, H, L, C` (chart candles, index = candle number), `T` (IST datetimes) and `mt` (tick 0.01). Usage (see `bese/sweep.py` `work()`):
`geng.prepare(tf, vw, src); geng._CUR['vw'] = vw; geng._CUR['src'] = src; ref_gbe.eprep = geng.ref_g.eprep; ref_gbe.run(tf, opts)`.
Settings of a catalogue strategy: `gold/crooks.py` `sources(tf)[i]['cfg']` (pop `vwAnchorG` -> vw, `vwSrcG` -> src, drop `p1`), on top of the
engine defaults `ref_gbe.IN`. Trade dict: `dir` (+1 long / -1 short), `fill` (candle of the fill), `entry`, `stop` (initial), `exit` (candle),
`res` (result in R), `ghost` (ignore ghost trades), `trig` ('be' / 'sv' / None).

Rules of a trade from its fill (risk = dir x (entry - initial stop); levels in price):
- Targets t1..t4 = entry + dir x tpkR x risk (k = 1..4, from opts / IN: tp1R 0.6, tp2R 1.0, tp3R 1.5, tp4R 2.0 unless set). Final target tF = t[exitAt].
- Fill candle: only the initial stop is checked (touched -> exit at -1R on the fill candle). No target, no trigger, no stop move on the fill candle.
- Every later candle, in this order:
  1. Exit check with the CURRENT stop and target: stop touched (long: low <= stop; short: high >= stop) -> exit at the stop; else target touched
     (long: high >= tF; short: low <= tF) -> exit at the target. Both touched on one candle -> the STOP. Tolerance 0.001 x tick.
     Result: a stop exit = dir x (stop - entry) / risk (-1 if the stop never moved); a target exit = exitR, except after a salvage
     trigger, when the target is the entry: 0.
  2. If no exit: the TP stop moves (when enabled: mv1On / mv2On / mv3On with mv1R / mv2R / mv3R): when this candle reaches t1 / t2 / t3 for the
     first time (long: high >= t_k), the stop moves to entry + dir x mvkR x risk if that is better than the current stop. From the next candle.
  3. If no exit and no trigger has acted yet in this trade: BE trigger (beOn, beR): the candle reaches entry + dir x beR x risk (long: high >=,
     short: low <=) -> the stop moves to the entry (only if better). Salvage trigger (svOn, svR): the candle reaches entry - dir x svR x risk (long:
     low <=, short: high >=) -> the final target becomes the entry. Only the FIRST of the two ever acts in a trade. If both are reached on the same
     candle: the extreme nearer the candle's open came first (|high - open| < |open - low| -> the high came first; for a long the high side is
     the BE side, for a short the low side is). From the next candle.
Costs are not part of `res`.

Task for the checker: write an independent implementation of these rules (do not import or copy `ref_gbe.py` logic) that, given the candles
and each trade's dir / fill / entry / initial stop and the settings, computes the exit candle, the exit kind and `res`; compare with
`ref_gbe.run` for every non-ghost trade.
