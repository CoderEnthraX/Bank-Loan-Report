# agentA: new intraday entry setups on gold (XAUUSD, FxPro), results

Scope: train 2021-01..2023-12 and valid 2024-01..2025-06 only. TEST was never touched (the kit default). All outcomes come from `kit.evaluate`
(1-minute path, stop checked first, every signal simulated on its own). "Excess" = hit% minus random market entries of the same direction in the same
split, averaged over TP1-TP4 (0.6 / 1 / 1.5 / 2 R). "Placebo-adj" = hit% minus a placebo built in `lib.placebo`: the same order geometry (entry offset and stop
distance in ATR, same mode and window), the same direction, the same split and the same New York hour, on 3 random bars per signal. It controls for the
time-of-day effect and for the stop-size and stop-entry mechanics.
Scripts: `lib.py` (helpers, placebo), `fam_orb.py`, `fam_sweep.py`, `fam_vwap.py`, `fam_time.py`, `fam_mr.py`, `fam_stop.py`, `candA.py`, `candB.py`,
`candCD.py`, `detail.py`, `boot.py`, `mt.py`, `make_table.py`. Raw rows are in `rows.jsonl` (screen) and `rows_cand.jsonl` (sensitivity); `detail.json` holds the finalists.

**Bottom line:** none of the 357 variants clearly beats random entries once the number of variants is taken into account. Two setups
come closest and hold up across their parameter neighbourhoods: A, the New York 09:30 opening-range stop entries, and B, the previous-day high/low sweep
with a confirmation stop entry. Their excess is about +3 to +7 points, but that is only z ≈ 2-2.5 (p ≈ 0.01-0.03 for each split). With this many
variants tried, results that strong are expected by chance. They are worth a look on TEST, not proven edges.

## Multiple-testing context (read before the table)
- 357 distinct variants (some rows repeat one rule under two names: the screen row and the "base" row of its sensitivity sweep). If no setup had an edge, about
  1/16 of them would show all 4 cells (train L, train S, valid L, valid S) > 0 by chance. 59 do, versus about 22 expected, but the variants are strongly correlated
  (neighbours of the same rule), so this is weak evidence.
- Pooled z (train+valid, L+S, SE 50/sqrt(n)) across all variants: mean +0.50, sd 1.05, max 2.8, **none above 3**. The +0.5 mean is a small systematic bias in
  the kit's excess: setups trade weekday active hours, while the baseline uses all bars. The placebo-adjusted columns remove most of it.
- Stop-entry rows (mode 2) show a systematic plus for shorts (+1.5..+2.8 on average across the 44 screen rows). Generic stop entries (random bars, C±k ATR or N-bar
  high/low, family 6) do **not** show it. So the plus is specific to stop orders at session structure (opening-range lows, data-bar lows, previous-day-sweep bars),
  and comes mostly from candidates A and B themselves, so it is not independent evidence.
- Verdict column: `FAIL` = at least one of the 4 cells <= 0; `all 4 > 0, z x` = all cells positive (z = pooled z; below 2 = noise level); `few trades` = below
  the README minimum (M5 20/mo, M15 8/mo, H1 3/mo of filled train trades). M1 could not be run: the kit has no `bars_M1.pkl` baseline. H1 was run where it fits.

## (1) Every setup tried
Columns: average excess (pts) over TP1-TP4, kit baseline; placebo-adjusted the same. n/mo = filled train trades per month, long+short.

