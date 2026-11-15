"""The strategy's 27 loss-recovery rules (port of Auction_Retest_Strategy.pine, section 2 + the risk formula in section 5).
Every trade is sized so that a stop-out loses exactly the computed $ risk INCLUDING the spread (like the strategy):
pnl = risk$ x (R - c) / (1 + c), c = spread / stop distance. Fractional sizes, no leverage limit, $10,000 start."""
import math
MODES = ['Off', 'Recover all losses on the next trade', 'Recover losses over N trades', 'Recover a % of losses per trade', 'Martingale (multiply after each loss)',
         'Exact recovery at final TP', 'Step-up (+$ per loss in a row)', 'Fibonacci', "D'Alembert", 'Rule C: carry the losses', 'Rule C split', 'Labouchere',
         'Grand Martingale', 'Paroli', "Reverse D'Alembert", 'Delayed recovery', '% of equity', "Oscar's Grind", 'Crooks A', 'Crooks B', 'Crooks C', 'Crooks D',
         'Crooks E', 'Crooks F', 'Crooks G', 'Crooks H', 'Crooks I', 'Crooks J']
# v4.5: Crooks C and the rules built on it (everything of Crooks C applies to them: over N wins, the rule after N losing recovery trades)
CFAM = ('Crooks C', 'Crooks E', 'Crooks F', 'Crooks G', 'Crooks H', 'Crooks I', 'Crooks J')
# v4.6 profit ladder (Crooks F - J): level -> (lock share of the highest profit, share of the cushion added to the base, most base x, most extra
# stop-out loss as a share of the cushion); the EA's ENUM_LADDER order (0 = off)
LADDER = {'Low': (0.8, 0.10, 2.0, 0.25), 'Medium': (0.7, 0.15, 3.0, 0.30), 'High': (0.6, 0.20, 5.0, 0.35), 'Extra high': (0.5, 0.25, 8.0, 0.40),
          'Max': (0.4, 0.30, 12.0, 0.50)}
LADFAM = ('Crooks F', 'Crooks G', 'Crooks H', 'Crooks I', 'Crooks J')
def lad_state(lad, ladT, net, peakNet, base):
    """the profit ladder: (on, guard, B, C). on once the highest closed profit reached ladT; guard = on and the closed profit at or below 0
    (every trade 0.01 lot); B = base + min((most - 1) x base, share x C); C = max(0, closed profit - lock x highest closed profit)"""
    if lad is None or peakNet < ladT: return False, False, base, 0.0
    lam, phi, bmax, gam = LADDER[lad]
    C = max(0.0, net - lam * peakNet)
    return True, net <= 0, base + min((bmax - 1.0) * base, phi * C), C
def simulate(trades, mode, base=50.0, cap=0.0, capAction='clamp', exitR=2.0, start=10000.0, recN=3, recPct=50.0, mult=2.0, step=25.0, cSplit=3, parN=3, delayN=2, eqPct=1.0, trace=None, cN=1,
             crkPr='off', crkPrN=2, crkPrPct=50.0, crkPrM=2, crkPrD=3, crkPrForget=False, fK=3.0, gX=10.0, hPct=1.0, jX=20.0, lad=None, ladT=1000.0):
    """trades: iterable of (R result, spread cost in R) or (R result, spread cost in R, parts) or (R, cost, parts, day events). parts = [(R of the part,
    share of the position)] for a trade with a partial close: Rule C's carried losses are then updated after each part, like the strategy (once per candle).
    v3.9 Crooks C rule after crkPrN losing recovery trades in a row (Crooks C only): crkPr 'forget' (new cycle), 'pct' (every recovery trade goes for
    crkPrPct % of the loss, the rest is forgotten when its last part wins; forget after N), 'wait' (no recovery trade until crkPrM wins in a row, then the
    first one needs a loss, then a win), 'skip' (no trades for the rest of the day and crkPrD counted days; crkPrForget = forget the loss). Day events: the
    new days (True = counted) that start before the trade, as the strategy / EA see them; a skipped trade adds 'SKIP' to the trace. The day events can
    also be a pair (since the previous signal's day, since the previous taken trade's exit day): the second is used after a taken trade.
    A 5th element (optional) is the leverage limit: the largest risk per $1 of equity (leverage x stop distance x (1 + cost) / entry price).
    v4.5 (Crooks C plus one change each; a 6th element (optional) is the $ risk of the Crooks E / I lot on this trade, e.g. 0.01 lot = 1 oz of
    gold: 1 x (stop distance + cost); without it those trades risk the base):
      Crooks E  while a loss is owed, a trade that is not the recovery trade is that lot, or the base if that is smaller
      Crooks F  a recovery trade risks at most fK x base (the rest of the loss is won back after the next wins, as Crooks C keeps a leftover)
      Crooks G  the loss to win back is at most gX x base (the rest is accepted as lost)
      Crooks H  a recovery trade risks at most hPct % of the equity (at least the base)
      Crooks I  Crooks E + Crooks F
      Crooks J  a recovery trade's risk x (1 - drawdown / (jX x base)), at least the base; drawdown = equity peak - equity (closed trades)
    v4.6 PROFIT LADDER (lad = 'Low' .. 'Max', Crooks F - J only; see lad_state): once the highest closed profit reached ladT, the rule works with
    the ladder base B; a trade risks at most the plain rule's risk + gam x C (the extra risk is paid from the cushion, never less than the plain
    rule); while the closed profit is at or below 0 every trade risks the 0.01 lot (the 6th element), or the base if that is smaller. Crooks G's
    limit is gX x the ladder base after the trade."""
    eq = start; peak = start; maxDD = 0.0; maxDDp = 0.0; net = 0.0; peakNet = 0.0      # peakNet: Crooks J (the drawdown of the closed profit)
    recPool = 0.0; recLosses = 0; dUnits = 1; carried = 0.0; lab = [1.0, 2.0, 3.0]; parWins = 0; rdUnits = 1; oscU = 1; oscP = 0.0
    capStop = False; n = 0; maxRisk = 0.0; maxRiskPct = 0.0; ruined = False; ruinAt = None; gp = gl = 0.0
    lossRun = 0.0; worstRun = 0.0; sumRisk = 0.0
    crL = 0.0; crN = 0; crW = False      # Crooks: $ loss to win back, closed trades in the cycle, the last trade won (Crooks C)
    crP = cN                             # Crooks C over N wins: parts of the loss still to win back (each recovery trade wins loss / parts)
    cfam = mode in CFAM
    prOn = cfam and crkPr != 'off'                               # v3.9 Crooks C rule after N losing recovery trades in a row
    crF = 0; crWait = False; crWW = 0; crNeedL = False; crSkip = False; crSkipLeft = 0; prevTaken = False
    for k, tr in enumerate(trades):
        res, c = tr[0], tr[1]; parts = tr[2] if len(tr) > 2 else None
        if capStop or ruined: break
        evs = tr[3] if len(tr) > 3 and tr[3] is not None else []      # a list of day events, or a pair of lists (see above)
        if isinstance(evs, tuple): evs = evs[1] if prevTaken else evs[0]
        for ev in evs:                                               # a new day while the skip rule pauses trading
            if not crSkip: break
            if crSkipLeft <= 0: crSkip = False
            elif ev: crSkipLeft -= 1
        if prOn and crkPr == 'skip' and crSkip:
            if trace is not None: trace.append('SKIP')
            prevTaken = False
            continue
        prevTaken = True
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
        # Crooks recovery trade: A / B trades 3, 5, 7 ... of a cycle; C the trade right after a win while a loss is owed; D trades 3, 6, 9 ...
        crRec = ((mode in (MODES[18], MODES[19]) and crN >= 2 and crN % 2 == 0) or (cfam and crW and crL > 0)
                 or (mode == MODES[21] and crN >= 2 and (crN - 2) % 3 == 0))
        if crRec and prOn and crkPr == 'wait' and (crWait or crNeedL): crRec = False
        r = {MODES[11]: base * labU, MODES[12]: base * mult ** min(recLosses, 200) + base * recLosses, MODES[13]: base * 2 ** parWins, MODES[14]: base * rdUnits,
             MODES[15]: (base + recPool / recN) if recLosses >= delayN else base, MODES[16]: eq * eqPct / 100.0, MODES[17]: base * min(oscU, oscNeed),
             MODES[4]: base * mult ** min(recLosses, 200), MODES[7]: base * (1.0 if recLosses == 0 else fb), MODES[8]: base * dUnits,
             MODES[9]: max(baseC, carried / cSplit), MODES[10]: max(baseC, carried / cSplit),
             MODES[18]: max(base, crL / exitR) if crRec else base, MODES[19]: max(base, crL / cSplit / exitR) if crRec else base,
             MODES[20]: max(base, crL / crP * (crkPrPct / 100.0 if prOn and crkPr == 'pct' else 1.0) / exitR) if crRec else base,
             MODES[21]: max(base, crL / exitR) if crRec else base}.get(mode, base + add)
        if cfam:                                                     # v4.5: Crooks C, and E - J built on it
            rmin = tr[5] if len(tr) > 5 else None
            def crk(B):
                x = max(B, crL / crP * (crkPrPct / 100.0 if prOn and crkPr == 'pct' else 1.0) / exitR) if crRec else B
                if crRec:
                    if mode in ('Crooks F', 'Crooks I'): x = min(x, fK * B)
                    elif mode == 'Crooks H': x = min(x, max(B, eq * hPct / 100.0))
                    elif mode == 'Crooks J': x = max(B, x * max(0.0, 1.0 - (peakNet - net) / (jX * B)))   # = peak - equity, exact at any start
                elif crL > 0 and mode in ('Crooks E', 'Crooks I') and rmin is not None: x = min(B, rmin)
                return x
            r = crk(base)
            lon, lguard, lB, lC = lad_state(lad if mode in LADFAM else None, ladT, net, peakNet, base)
            if lon:                                                  # v4.6 profit ladder
                r = min(crk(lB), r + LADDER[lad][3] * lC)
                if lguard: r = min(base, rmin) if rmin is not None else base
        if cap > 0 and r > cap:
            if capAction == 'stop': capStop = True; break
            elif capAction == 'reset':
                recPool = 0.0; recLosses = 0; dUnits = 1; carried = 0.0; lab = [1.0, 2.0, 3.0]; parWins = 0; rdUnits = 1; oscU = 1; oscP = 0.0
                crL = 0.0; crN = 0; crRec = False; crW = False; crP = cN; crF = 0; crWait = False; crWW = 0; crNeedL = False
                r = min(baseC, cap)
            else: r = cap
        levk = tr[4] if len(tr) > 4 else None                       # the leverage limit (the strategy's 1:100 by default)
        if levk is not None and eq > 0: r = min(r, eq * levk)
        if trace is not None: trace.append(r)
        maxRisk = max(maxRisk, r); maxRiskPct = max(maxRiskPct, r / eq if eq > 0 else 9.99); sumRisk += r
        pnl = r * (res - c) / (1.0 + c); n += 1
        eq += pnl; net += pnl
        if pnl > 0: gp += pnl
        else: gl -= pnl
        lossRun = lossRun + pnl if pnl < 0 else 0.0; worstRun = min(worstRun, lossRun)
        peak = max(peak, eq); dd = peak - eq; maxDD = max(maxDD, dd); maxDDp = max(maxDDp, dd / peak); peakNet = max(peakNet, net)
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
        # Crooks: losses add to the loss to win back, wins reduce it; a new cycle when it is all back (A, D: also when a recovery trade wins;
        # C keeps a leftover: a recovery trade that wins without winning everything back is followed by another recovery trade)
        lastPart = crP == 1                                            # this recovery trade went for the last part of the loss
        crL = max(0.0, crL - pnl)
        if mode == 'Crooks G': crL = min(crL, gX * lad_state(lad, ladT, net, peakNet, base)[2])   # v4.5: never more than gX x base (v4.6: the ladder base)
        if crL < 0.01 or (mode in (MODES[18], MODES[21]) and win and crRec):      # less than a cent left = all won back
            crL = 0.0; crN = 0; crP = cN; crF = 0; crWait = False; crWW = 0; crNeedL = False
        else:
            crN += 1
            crP = cN if not win else (max(1, crP - 1) if crRec else crP)     # a loss starts the N parts again after the next win
            if prOn:
                if crWait:                                             # wait rule: M wins in a row end the wait, then a loss is needed
                    crWW = crWW + 1 if win else 0
                    if crWW >= crkPrM: crWait = False; crWW = 0; crNeedL = True
                elif crNeedL and not win: crNeedL = False
                if crRec and win:
                    crF = 0
                    if crkPr == 'pct' and lastPart: crL = 0.0; crN = 0; crP = cN    # the % went for is back, the rest is forgotten
                elif crRec:
                    crF += 1
                    if crF >= crkPrN:
                        crF = 0
                        if crkPr in ('forget', 'pct'): crL = 0.0; crN = 0; crP = cN
                        elif crkPr == 'wait': crWait = True; crWW = 0; crNeedL = False
                        elif crkPr == 'skip':
                            crSkip = True; crSkipLeft = crkPrD
                            if crkPrForget: crL = 0.0; crN = 0; crP = cN
        crW = win
    return dict(mode=mode, trades=n, avgRisk=sumRisk / n if n else 0.0, net=net, end=eq, maxDD=maxDD, maxDDpct=maxDDp, maxRisk=maxRisk, maxRiskPct=maxRiskPct, ruined=ruined, ruinAt=ruinAt,
                pf=(gp / gl) if gl > 0 else float('inf'), worstRun=-worstRun, capStopped=capStop)
def risks(trades, mode, **kw):
    """the $ risk of each trade (for hand checks): re-runs the simulation on growing prefixes"""
    out = []
    for i in range(1, len(trades) + 1):
        a = simulate(trades[:i - 1], mode, **kw)['avgRisk'] * (i - 1) if i > 1 else 0.0
        b = simulate(trades[:i], mode, **kw)['avgRisk'] * i
        out.append(round(b - a, 6))
    return out
if __name__ == '__main__':
    # sanity: Off on a +2/-1 sequence with no costs
    t = [(2.0, 0.0), (-1.0, 0.0), (-1.0, 0.0), (2.0, 0.0)]
    for m in (MODES[0], MODES[1], MODES[4]):
        print(m, simulate(t, m))
