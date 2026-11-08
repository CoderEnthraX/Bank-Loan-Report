# of_agentB progress (order-flow entries on gold)
## Step 0 (done): read README_KIT, kit.py, of.py, agentA results/lib. Plan: lib.py wraps agentA/lib (ctx, placebo same NY hour, run) writing rows to of_agentB/rows.jsonl.
Families: F1 absorption at VA edges, F2 failed auction / 80% rule, F3 LVN/HVN, F4 POC reversion/migration, F5 delta/CVD, F6 combos with signals.raw.
Next: step 1 = write lib.py + sanity check of.flow on M5/M15.
## Step 1 (done): oflib.py (ctx with OF arrays, session/prior H-L, rvol_t = vol / same-NY-time 20-session mean; orders/variants: mkt|stp x atr 1.8|struct; run -> rows.jsonl with placebo same NY hour K=3)
## Step 2 (done): fam12.py F1 absorption (pVA/dVA, +opp delta) and F2 failed auction prior VA (+accepted), 80% rule (session / NY0930 anchor), M15 + M5. 64 variants.
 - Absorption strict (rvol_t>=1.5, range<=1.3ATR, CLV rejection): only 0.4-6/mo, noisy, mostly negative. FAIL.
 - failVA: M15 train all neg (-0.4..-2.6). M5 'accepted stp struct' all 4 >0 but +1.0/+1.1 train, +1.4/+5.7 valid (z<1): noise.
 - 80% rule: 2-7/mo, train mixed. FAIL.
Next: step 3 = loose absorption + F3 LVN/HVN (composite profile) script fam3.py.
## Step 3 (done): fam3.py (oflib.comp_rvp = composite profile of 5 prior sessions). F1b loose absorption (rvol_t>=1.2) and F3 (brk12 LVN-ahead / HVN-ahead / all, LVN reject, HVN hold + nonHVN ctrl), M15+M5: 72 variants.
 - F1b: M15 pVA train L +5..+7 but valid L -0.5..-3.9 FAIL; M5 dVA stp struct +3.1/-0.0/+2.1/+5.8 (train S 0) FAIL.
 - F3 breakout: LVN-ahead == HVN-ahead == all (all ~ -1..+1 train): LVN 'fast travel' has no effect. LVN reject 3-5/mo noisy. HVN hold: no better than non-HVN control.
 - only all-4>0: M5 'nonHVN hold (ctrl)' stp atr +0.9/+1.9/+0.8/+0.7 (placebo adj ~0): noise.
Next: step 4 = fam45.py F4 POC reversion / migration, F5 delta/CVD (divergence at session extreme, delta flip after sweep, climax+opp delta, IB breakout + CVD).
## Step 4 (done): fam45.py F4 (POC reversion dev/prior at 90th pct distance +-revbar; POC migration pullback / trend) and F5 (CVD divergence tk/cl +-rej, CVD-confirm controls, delta flip after sweep, climax+opp delta vs aligned ctrl, IB breakout CVD agree/disagree), M15+M5: 132 variants. Total so far ~268.
 - all-4>0 worth a look: M5 'F4 POCrev dPOC k8.7 mkt atr' +5.0/+1.1/+5.1/+0.3 (pl +3.7/+0.3/+1.0/+2.6) n~977/974 train; mkt struct +1.1/+1.8/+2.4/+3.1 but E1 -0.40.
   M5 'F5 CVDdiv cl stp struct' +2.4/+2.2/+1.6/+5.4 (pl +5.6/+2.1/+1.3/+5.1) n 380/500; but M15 same rule FAILS (-4.1 train L) -> TF-inconsistent.
   M15 'F5 CVDdiv cl +rej mkt atr' +2.1/+2.6/+2.4/+3.2 n~190 (se 3.6).
 - delta flip, climax opp delta (1-2/mo), IB+CVD agree: FAIL. IB breakout CVD agree no better than disagree.
Next: step 5 = score.py (count all-4>0, pooled z over rows.jsonl), then fam6.py combos with signals.raw.
## Step 5 (done): fam6.py: indicator raw signals (M15 6487, M5 17542) x OF filters (bar delta agrees [96-98% of signals], sess CVD agrees [80-85%], close beyond dev VA, dev POC ahead [1-2%], LVN path ahead, beyond prior VA) x (lim own / mkt / stp), + NOT subsets + OPP trade on NOT. ~124 variants. Nothing passes: all within +-2, signs flip train/valid. score.py: see below.
Next: step 6 = cand.py sensitivity for C1 (POCrev dPOC M5) and C2 (CVDdiv cl M5 stp): k / gap / TF (M1, M15, H1) / per-year / VWAP-distance control.
## Step 6a (done): cand.py c1 (threshold from TRAIN pct) M5/M15/H1 -> cand_c1.out. C1 = long-only effect: M5 longs train +1.8..+6.9, valid +0.4..+7.2 across pct 80-95/gap/minsess/stop size; shorts ~0 (-0.7..+1.9 train, -5..+1.6 valid). M15 longs train +1.3..+3.2, valid -2.4..+3.2; shorts neg. H1 longs valid neg. VWAP control M5 L +3.4/-0.1; /SD normalisation fails. => C1 not a two-sided edge; longs on M5 only.
Next: step 6b = cand.py c2 M5 M15 H1 (+M1 later).
## Step 6b (done): cand_c2.out. C2 (CVD-CLV divergence at new session extreme, stop entry) M5: all 7 cl variants all-4>0 (+0.3..+5.4), tk weaker (valid ~+1). M15 and H1: valid NEGATIVE for every variant (-1..-15). => M5-only.
Next: step 6c = M1 check of C1/C2 (cand_m1.py), then per-year + per-TP detail (detail.py).
## Step 6c (done): cand_m1.out. C2 on M1 (m 15/30/60): ALL cells negative (-0.7..-7) -> C2 = M5-only = noise. C1 on M1 p90 +1.7/+0.4/+0.4/+0.3, p95 +1.5/+0.7/+4.2/+1.7 but E1 -0.47 (spread).
Next: step 7 = detail.py (per TP, per year, placebo, E) for C1 M5 p90 mkt atr, C1 M5 p90 long-only, C2 M5 cl m6 stp struct.
## Step 7 (done): detail.out / detail.json. C1 M5 p90 mkt 1.8ATR: LONG train +5.0 (pl +3.5) valid +4.1 (pl +2.2), every year +3.2..+5.9; SHORT train +1.1, valid -0.3, years -0.7..+3.0. E longs TP1 -0.04/+0.04, TP4 +0.02/+0.22. M15 same rule: L +2.1/+1.2, S -0.9/-3.0.
 C2 M5: train L +2.4 S +2.2, valid L +1.6 S +5.4 (se 2.6-3.8), E TP1 -0.11 train; fails M1/M15/H1.
Next: step 8 = fam6b.py: C1 x indicator signals (signal toward POC when far; opposite trade when signal runs away from POC), then results.md.
## Step 8 (done): fam6b.out. NEW candidate C3 = indicator raw signal that points AWAY from the developing POC while |C - dPOC| >= p80 (train) in ATR (M5 k 5.8, M15 k 3.4) -> take the OPPOSITE trade at market, 1.8 ATR stop.
 M5: train L +5.2 S +4.5, valid L +3.3 S +3.4 (placebo +5.3/+3.8/+2.2/+4.2), n 2509 train (69.7/mo), NOT declustered. M15: -0.5/+1.2/+1.9/+1.1 (weak). Stop-entry variant weaker.
 score: 443 variants, all4>0 31 (exp ~28), max z 5.41 (C3 M5).
Next: step 9 = c3.py sensitivity: decluster, pct 70/80/90, stop 1.2/2.5, NOT-far control, generic impulse-bar-away control, M1/H1, per year.
## Step 9 (done): c3.out. C3 robust on M5 (every variant all-4>0: pct 70-95, stop 1.2/2.5 ATR, minsess0, declustered gap 12: p80 +5.1/+4.6/+5.2/+2.6), M1 mostly all-4>0 (+0.6..+5.2, E -0.3 spread), H1 p80 +1.8/+3.0/+2.7/+6.7, M15 WEAK (-0.8/+1.7/+1.2/+0.3). Control NEAR-POC OPP ~0/neg. Generic impulse bar (body>=0.8ATR, close outer 25%) away from POC, faded: M5 +2.2/+3.5/+4.5/+1.1, M15 +1.9/+2.0/+1.6/+1.9 -> phenomenon = exhaustion fade of an extension bar far from session value. VWAP-dist version also works on M5.
Next: step 10 = check agentA overlap (VWAP fades), detail of C3 (per TP, per year, E), then results.md.
## Step 10a (done): agentA overlap: agentA |C-VWAP|>6ATR fade M5 was +2.0/+2.8/+5.0/+1.5 (z 2.6); VWAP sigma fades failed. C3 = that idea + an impulse (indicator) bar in the extension direction; stronger, esp. shorts.
Next: step 10b = c3delta.py (does delta/CVD add to C3?) + c3 detail; then results.md.
## Step 10b (done): c3delta.out: bar-delta strength / CVD divergence split of C3 makes no consistent difference (both halves +2..+7) -> delta adds nothing. Next: detail3.py (C3 M5/M1/H1/M15 + generic) then results.md
## Step 11 (done): detail3.out/json. C3 M5 p80 declust: every TP x split x dir excess > 0 (train L +4.0..+5.9 S +3.7..+5.8; valid L +4.0..+5.7 S +2.2..+3.1), placebo-adj all > 0, every year x dir > 0 (+0.3..+9.0), 43/mo train, E TP1 -0.05 / TP4 +0.06 train. M1: L +3.8/+1.4, S +0.9/+3.1 (E -0.3, spread). H1: +1.8/+3.1/+2.7/+6.7 (7-10/mo). M15: -0.8/+1.7/+1.2/+0.3 (weak). Generic impulse version M5 +2.2/+3.5/+4.5/+1.1, M15 +1.9/+2.0/+1.6/+1.9.
Next: step 12 = boot.py (month-block bootstrap of C3 M5 / C3gen), then write results.md.
## Step 12 (done): boot.out month-block bootstrap: C3 M5 train both z 4.1 (L 3.5, S 2.7), valid both z 2.6 (L 2.4, S 1.3). C3gen M5 train z 2.3 valid 1.6. H1 C3 z 1.4/1.8. Next: make_table.py -> table.md, then results.md
## Step 13 (done): results.md written (head.md + table.md + tail.md + cands.md + concl.md). DONE.
