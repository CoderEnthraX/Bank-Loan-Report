"""The strategy's 27 loss-recovery rules (port of Auction_Retest_Strategy.pine, section 2 + the risk formula in section 5).
Every trade is sized so that a stop-out loses exactly the computed $ risk INCLUDING the spread (like the strategy):
pnl = risk$ x (R - c) / (1 + c), c = spread / stop distance. Fractional sizes, no leverage limit, $10,000 start."""
import math
MODES = ['Off', 'Recover all losses on the next trade', 'Recover losses over N trades', 'Recover a % of losses per trade', 'Martingale (multiply after each loss)',
         'Exact recovery at final TP', 'Step-up (+$ per loss in a row)', 'Fibonacci', "D'Alembert", 'Rule C: carry the losses', 'Rule C split', 'Labouchere',
         'Grand Martingale', 'Paroli', "Reverse D'Alembert", 'Delayed recovery', '% of equity', "Oscar's Grind", 'Crooks A', 'Crooks B', 'Crooks C', 'Crooks D',
         'Crooks E', 'Crooks F', 'Crooks G', 'Crooks H', 'Crooks I', 'Crooks J', 'Crooks K', 'Crooks L', 'Crooks X']
# v4.5: Crooks C and the rules built on it (everything of Crooks C applies to them: over N wins, the rule after N losing recovery trades)
CFAM = ('Crooks C', 'Crooks E', 'Crooks F', 'Crooks G', 'Crooks H', 'Crooks I', 'Crooks J', 'Crooks K', 'Crooks L', 'Crooks X')   # v5.0: + K, L; v5.2: + X
# v4.6 profit ladder (Crooks F - J): level -> (lock share of the highest profit, share of the cushion added to the base, most base x, most extra
# stop-out loss as a share of the cushion); the EA's ENUM_LADDER order (0 = off)
LADDER = {'Low': (0.8, 0.10, 2.0, 0.25), 'Medium': (0.7, 0.15, 3.0, 0.30), 'High': (0.6, 0.20, 5.0, 0.35), 'Extra high': (0.5, 0.25, 8.0, 0.40),
          'Max': (0.4, 0.30, 12.0, 0.50)}
LADFAM = ('Crooks F', 'Crooks G', 'Crooks H', 'Crooks I', 'Crooks J', 'Crooks K')   # v5.0: + K
def lad_state(lad, ladT, net, peakNet, base):
    """the profit ladder: (on, guard, B, C). on once the highest closed profit reached ladT; guard = on and the closed profit at or below 0
    (every trade 0.01 lot); B = base + min((most - 1) x base, share x C); C = max(0, closed profit - lock x highest closed profit)"""
    if lad is None or peakNet < ladT: return False, False, base, 0.0
    lam, phi, bmax, gam = LADDER[lad]
    C = max(0.0, net - lam * peakNet)
    return True, net <= 0, base + min((bmax - 1.0) * base, phi * C), C
def simulate(trades, mode, base=50.0, cap=0.0, capAction='clamp', exitR=2.0, start=10000.0, recN=3, recPct=50.0, mult=2.0, step=25.0, cSplit=3, parN=3, delayN=2, eqPct=1.0, trace=None, cN=1,
             crkPr='off', crkPrN=2, crkPrPct=50.0, crkPrM=2, crkPrD=3, crkPrForget=False, fK=3.0, gX=10.0, hPct=1.0, jX=20.0, lad=None, ladT=1000.0, baseMode='usd', basePct=1.0,
             sizeBy='risk', kMode='lots', kUsd=25.0, kPct=50.0, lZ1=2.0, lZ1N=6, lZ2=5.0, lZ2N=3, lGrow=10.0, lGrowX=4.0, xStep=1000.0, xLim=0.0):
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
    limit is gX x the ladder base after the trade.
    v4.7 position size: baseMode 'usd' (base), 'pct' (basePct % of the equity before the trade) or 'lot' (the 7th element of each trade: the $ the
    fixed lots lose at that trade's stop); the rule sizes every trade from it, and a trade is booked with its own base (Oscar's Grind, Crooks G).
    v5.0 (v50/SPEC_v50.md): sizeBy 'profit': the base (usd / pct) and every amount a rule adds are the WIN at the final TP: divided by exitR
    (D); Oscar's goal is one base win. Crooks K (Crooks J + ladder above the zero line; below it the careful size after a win: kMode 'lots'
    = the 8th element (the careful lots' $ risk), 'usd' = kUsd / D, 'pct' = kPct % of the base; after a loss the 0.01 lot). Crooks L (the
    0.01 lot while waiting; the parts of a loss set when it is booked: lZ1 / lZ1N below the start, lZ2 / lZ2N below the best; at a new best
    the base grows lGrow % of the profit / D, at most lGrowX x).
    v5.1: with profit D = the 9th element of the trade (a final-TP win per $ of stop-out loss on that setup, costs included; absent: exitR),
    used for every amount (also Exact and the Crooks recovery, which divide by exitR in Risk mode).
    v5.2 Crooks X (SPEC section 6): Crooks E with the loss to win back SET after every close from the levels: below the start the gap to it,
    above it the gap to the next xStep level (at most the best); a win into another step starts N parts again; xLim > 0: a recovery trade risks
    at most max(base, xLim)."""
    eq = start; peak = start; maxDD = 0.0; maxDDp = 0.0; net = 0.0; peakNet = 0.0      # peakNet: Crooks J (the drawdown of the closed profit)
    recPool = 0.0; recLosses = 0; dUnits = 1; carried = 0.0; lab = [1.0, 2.0, 3.0]; parWins = 0; rdUnits = 1; oscU = 1; oscP = 0.0
    capStop = False; n = 0; maxRisk = 0.0; maxRiskPct = 0.0; ruined = False; ruinAt = None; gp = gl = 0.0
    lossRun = 0.0; worstRun = 0.0; sumRisk = 0.0
    crL = 0.0; crN = 0; crW = False      # Crooks: $ loss to win back, closed trades in the cycle, the last trade won (Crooks C)
    cN = 1 if mode == 'Crooks L' else cN   # v5.0 Crooks L: its parts come from the drawdown (over N wins is not used)
    crP = cN                             # Crooks C over N wins: parts of the loss still to win back (each recovery trade wins loss / parts)
    pm = sizeBy == 'profit'                # v5.0 Size By profit (v5.1: D per trade, below)
    cfam = mode in CFAM
    prOn = cfam and crkPr != 'off'                               # v3.9 Crooks C rule after N losing recovery trades in a row
    crF = 0; crWait = False; crWW = 0; crNeedL = False; crSkip = False; crSkipLeft = 0; prevTaken = False
    def xidx(v): return -1 if v < -0.005 else math.floor((v + 0.005) / xStep)   # v5.2 Crooks X: the step the closed profit is in
    def xtarget(v):                      # v5.2 Crooks X: the loss to win back from the levels (start, steps, best)
        if v < -0.005: return -v
        if v >= peakNet - 0.005: return 0.0
        return max(0.0, min(peakNet, (math.floor((v + 0.005) / xStep) + 1) * xStep) - v)
    def lparts(bb):                      # v5.0 Crooks L: the parts of the loss just booked (net / peakNet after it)
        if net < 0: dd, st_, mx = -net, lZ1 * bb, max(1, lZ1N)
        elif net < peakNet: dd, st_, mx = peakNet - net, lZ2 * bb, max(1, lZ2N)
        else: return 1
        return int(max(1, min(mx, math.ceil(dd / st_ - 1e-9)))) if st_ > 0 else 1
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
        b = base if baseMode == 'usd' else (max(0.0, eq) * basePct / 100.0 if baseMode == 'pct' else tr[6])   # v4.7: this trade's base ($ / % of equity / fixed lots' $, the 7th element)
        Dt = (tr[8] if len(tr) > 8 and tr[8] is not None else exitR) if pm else exitR   # v5.1: a final-TP win per $ of stop-out loss (this setup)
        D = Dt if pm else 1.0; XR = Dt if pm else exitR                  # amounts / D; Exact and the Crooks recovery / XR (Risk: exitR)
        if pm and baseMode != 'lot': b = b / D                           # v5.0: the base is the win at the final TP
        add = recPool / D if mode == MODES[1] else recPool / recN / D if mode == MODES[2] else recPool * recPct / 100 / D if mode == MODES[3] else recPool / XR if mode == MODES[5] else step * recLosses / D if mode == MODES[6] else 0.0
        fa = fb = 1.0
        for _ in range(2, min(recLosses, 200) + 1): fa, fb = fb, fa + fb   # capped: beyond ~200 losses every rule is far past any cap or account
        prof = net; stepBase = 0.0
        if prof >= 1000: kk = math.floor((prof - 1000) / 500); stepBase = (1000.0 + 500.0 * kk) / (8 + kk)
        elif prof >= 500: stepBase = 500.0 / 5
        elif prof >= 200: stepBase = 200.0 / 3
        stepBase = stepBase / D                                         # v5.0: a base amount
        baseC = max(b, min(stepBase, cap) if cap > 0 else stepBase) if mode == MODES[10] else b
        labU = lab[0] + lab[-1] if len(lab) > 1 else lab[0]
        oscNeed = int(max(1, math.ceil(((b * D if pm else b) - oscP) / (b * XR))))   # v5.0: with profit the goal is one base win (v5.1: x D)
        # Crooks recovery trade: A / B trades 3, 5, 7 ... of a cycle; C the trade right after a win while a loss is owed; D trades 3, 6, 9 ...
        crRec = ((mode in (MODES[18], MODES[19]) and crN >= 2 and crN % 2 == 0) or (cfam and crW and crL > 0)
                 or (mode == MODES[21] and crN >= 2 and (crN - 2) % 3 == 0))
        if crRec and prOn and crkPr == 'wait' and (crWait or crNeedL): crRec = False
        r = {MODES[11]: b * labU, MODES[12]: b * mult ** min(recLosses, 200) + b * recLosses, MODES[13]: b * 2 ** parWins, MODES[14]: b * rdUnits,
             MODES[15]: (b + recPool / recN / D) if recLosses >= delayN else b, MODES[16]: eq * eqPct / 100.0 / D, MODES[17]: b * min(oscU, oscNeed),
             MODES[4]: b * mult ** min(recLosses, 200), MODES[7]: b * (1.0 if recLosses == 0 else fb), MODES[8]: b * dUnits,
             MODES[9]: max(baseC, carried / cSplit / D), MODES[10]: max(baseC, carried / cSplit / D),
             MODES[18]: max(b, crL / XR) if crRec else b, MODES[19]: max(b, crL / cSplit / XR) if crRec else b,
             MODES[20]: max(b, crL / crP * (crkPrPct / 100.0 if prOn and crkPr == 'pct' else 1.0) / XR) if crRec else b,
             MODES[21]: max(b, crL / XR) if crRec else b}.get(mode, b + add)
        if cfam:                                                     # v4.5: Crooks C, and E - J built on it
            rmin = tr[5] if len(tr) > 5 else None
            def crk(B):
                x = max(B, crL / crP * (crkPrPct / 100.0 if prOn and crkPr == 'pct' else 1.0) / XR) if crRec else B
                if crRec:
                    if mode in ('Crooks F', 'Crooks I'): x = min(x, fK * B)
                    elif mode == 'Crooks H': x = min(x, max(B, eq * hPct / 100.0))
                    elif mode in ('Crooks J', 'Crooks K'): x = max(B, x * max(0.0, 1.0 - (peakNet - net) / (jX * B)))   # = peak - equity, exact at any start (v5.0: K too)
                    elif mode == 'Crooks X' and xLim > 0: x = min(x, max(B, xLim))      # v5.2 Crooks X: the per-trade limit
                elif crL > 0 and mode in ('Crooks E', 'Crooks I', 'Crooks L', 'Crooks X') and rmin is not None: x = min(B, rmin)   # v5.0: L waits with the lot too (v5.2: X)
                return x
            bL = b                                                    # v5.0 Crooks L: at a new best the base grows with the profit
            if mode == 'Crooks L' and net >= peakNet: bL = b + min((max(1.0, lGrowX) - 1.0) * b, max(0.0, lGrow / 100.0 * net / D))
            r = crk(bL)
            lon, lguard, lB, lC = lad_state(lad if mode in LADFAM else None, ladT, net, peakNet, b)
            if lon:                                                  # v4.6 profit ladder
                r = min(crk(lB), r + LADDER[lad][3] * lC)
                if lguard and mode != 'Crooks K': r = min(b, rmin) if rmin is not None else b   # v5.0: no start guard for K (its zone)
            if mode == 'Crooks K' and net < 0:                        # v5.0 Crooks K below the zero line: careful after a win, else the lot
                if crW:
                    kr = tr[7] if len(tr) > 7 and tr[7] is not None and tr[7] > 0 else None
                    r = (kUsd / D) if kMode == 'usd' else (b * kPct / 100.0) if kMode == 'pct' else (kr if kr is not None else b)
                else: r = min(b, rmin) if rmin is not None else b
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
        if oscP >= (b * D if pm else b): oscU = 1; oscP = 0.0            # v5.0: with profit the goal is one base win (v5.1: x D)
        elif win: oscU += 1
        # Crooks: losses add to the loss to win back, wins reduce it; a new cycle when it is all back (A, D: also when a recovery trade wins;
        # C keeps a leftover: a recovery trade that wins without winning everything back is followed by another recovery trade)
        lastPart = crP == 1                                            # this recovery trade went for the last part of the loss
        crL = max(0.0, crL - pnl)
        xNew = False
        if mode == 'Crooks X': crL = xtarget(net); xNew = win and xidx(net - pnl) != xidx(net)   # v5.2: set from the levels; a new step
        if mode == 'Crooks G': crL = min(crL, gX * lad_state(lad, ladT, net, peakNet, b)[2])   # v4.5: never more than gX x b (v4.6: the ladder b)
        if crL < 0.01 or (mode in (MODES[18], MODES[21]) and win and crRec):      # less than a cent left = all won back
            crL = 0.0; crN = 0; crP = cN; crF = 0; crWait = False; crWW = 0; crNeedL = False
        else:
            crN += 1
            crP = (lparts(b) if mode == 'Crooks L' else cN) if not win else (max(1, crP - 1) if crRec else crP)     # a loss starts the N parts again after the next win (v5.0 L: from the drawdown)
            if xNew: crP = cN                                          # v5.2 Crooks X: a new step is won back in N trades
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
