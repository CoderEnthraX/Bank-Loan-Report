"""The strategy's 17 loss-recovery rules (port of Auction_Retest_Strategy.pine, section 2 + the risk formula in section 5).
Every trade is sized so that a stop-out loses exactly the computed $ risk INCLUDING the spread (like the strategy):
pnl = risk$ x (R - c) / (1 + c), c = spread / stop distance. Fractional sizes, no leverage limit, $10,000 start."""
import math
MODES = ['Off', 'Recover all losses on the next trade', 'Recover losses over N trades', 'Recover a % of losses per trade', 'Martingale (multiply after each loss)',
         'Exact recovery at final TP', 'Step-up (+$ per loss in a row)', 'Fibonacci', "D'Alembert", 'Rule C: carry the losses', 'Rule C split', 'Labouchere',
         'Grand Martingale', 'Paroli', "Reverse D'Alembert", 'Delayed recovery', '% of equity', "Oscar's Grind"]
def simulate(trades, mode, base=50.0, cap=0.0, capAction='clamp', exitR=2.0, start=10000.0, recN=3, recPct=50.0, mult=2.0, step=25.0, cSplit=3, parN=3, delayN=2, eqPct=1.0):
    """trades: iterable of (R result, spread cost in R) or (R result, spread cost in R, parts). parts = [(R of the part, share of the position)]
    for a trade with a partial close: Rule C's carried losses are then updated after each part, like the strategy (once per candle)."""
    eq = start; peak = start; maxDD = 0.0; maxDDp = 0.0; net = 0.0
    recPool = 0.0; recLosses = 0; dUnits = 1; carried = 0.0; lab = [1.0, 2.0, 3.0]; parWins = 0; rdUnits = 1; oscU = 1; oscP = 0.0
    capStop = False; n = 0; maxRisk = 0.0; maxRiskPct = 0.0; ruined = False; ruinAt = None; gp = gl = 0.0
    lossRun = 0.0; worstRun = 0.0; sumRisk = 0.0
    for k, tr in enumerate(trades):
        res, c = tr[0], tr[1]; parts = tr[2] if len(tr) > 2 else None
        if capStop or ruined: break
        add = recPool if mode == MODES[1] else recPool / recN if mode == MODES[2] else recPool * recPct / 100 if mode == MODES[3] else recPool / exitR if mode == MODES[5] else step * recLosses if mode == MODES[6] else 0.0
        fa = fb = 1.0
        for _ in range(2, min(recLosses, 200) + 1): fa, fb = fb, fa + fb   # capped: beyond ~200 losses every rule is far past any cap or account
        prof = net; stepBase = 0.0
        if prof >= 1000: kk = math.floor((prof - 1000) / 500); stepBase = (1000.0 + 500.0 * kk) / (8 + kk)
        elif prof >= 500: stepBase = 500.0 / 5
        elif prof >= 200: stepBase = 200.0 / 3
        baseC = max(base, min(stepBase, cap) if cap > 0 else stepBase) if mode == MODES[10] else base
        labU = lab[0] + lab[-1] if len(lab) > 1 else lab[0]
        oscNeed = int(max(1, math.ceil((base - oscP) / (base * exitR))))
        r = {MODES[11]: base * labU, MODES[12]: base * mult ** min(recLosses, 200) + base * recLosses, MODES[13]: base * 2 ** parWins, MODES[14]: base * rdUnits,
             MODES[15]: (base + recPool / recN) if recLosses >= delayN else base, MODES[16]: eq * eqPct / 100.0, MODES[17]: base * min(oscU, oscNeed),
             MODES[4]: base * mult ** min(recLosses, 200), MODES[7]: base * (1.0 if recLosses == 0 else fb), MODES[8]: base * dUnits,
             MODES[9]: max(baseC, carried / cSplit), MODES[10]: max(baseC, carried / cSplit)}.get(mode, base + add)
        if cap > 0 and r > cap:
            if capAction == 'stop': capStop = True; break
            elif capAction == 'reset':
                recPool = 0.0; recLosses = 0; dUnits = 1; carried = 0.0; lab = [1.0, 2.0, 3.0]; parWins = 0; rdUnits = 1; oscU = 1; oscP = 0.0
                r = min(baseC, cap)
            else: r = cap
        maxRisk = max(maxRisk, r); maxRiskPct = max(maxRiskPct, r / eq if eq > 0 else 9.99); sumRisk += r
        pnl = r * (res - c) / (1.0 + c); n += 1
        eq += pnl; net += pnl
        if pnl > 0: gp += pnl
        else: gl -= pnl
        lossRun = lossRun + pnl if pnl < 0 else 0.0; worstRun = min(worstRun, lossRun)
        peak = max(peak, eq); dd = peak - eq; maxDD = max(maxDD, dd); maxDDp = max(maxDDp, dd / peak)
        if eq <= 0: ruined = True; ruinAt = k
        win = pnl > 0
        if parts:
            for pr, pw in parts: carried = max(0.0, carried - r * (pr - pw * c) / (1.0 + c))
        else: carried = max(0.0, carried - pnl)
        if win:
            recPool = max(0.0, recPool - pnl); recLosses = recLosses if recPool > 0 else 0
            dUnits = max(1, dUnits - 1); rdUnits += 1; parWins = 0 if parWins + 1 >= parN else parWins + 1
            if lab: lab.pop(0)
            if lab: lab.pop()
            if not lab: lab = [1.0, 2.0, 3.0]
        else:
            recPool += -pnl; recLosses += 1; dUnits += 1; rdUnits = max(1, rdUnits - 1); parWins = 0
            lab.append(lab[0] + lab[-1] if len(lab) > 1 else lab[0])
        oscP += pnl
        if oscP >= base: oscU = 1; oscP = 0.0
        elif win: oscU += 1
    return dict(mode=mode, trades=n, avgRisk=sumRisk / n if n else 0.0, net=net, end=eq, maxDD=maxDD, maxDDpct=maxDDp, maxRisk=maxRisk, maxRiskPct=maxRiskPct, ruined=ruined, ruinAt=ruinAt,
                pf=(gp / gl) if gl > 0 else float('inf'), worstRun=-worstRun, capStopped=capStop)
if __name__ == '__main__':
    # sanity: Off on a +2/-1 sequence with no costs
    t = [(2.0, 0.0), (-1.0, 0.0), (-1.0, 0.0), (2.0, 0.0)]
    for m in (MODES[0], MODES[1], MODES[4]):
        print(m, simulate(t, m))
