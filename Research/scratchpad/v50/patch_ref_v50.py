"""v5.0 reference (SPEC_v50.md): gold/recovery.py and gold/crooks_tp1.py from their v4.9 copies (gold/*_v49.py):
Size By (risk / profit), Crooks K, Crooks L. Risk mode with the old rules = v4.9 exactly (checked by v50/ref_regress.py)."""
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
G = S + '/gold/'


def sub(s, a, b, n=1):
    assert s.count(a) == n, (a[:100], s.count(a))
    return s.replace(a, b)


# ---------------------------------------------------------------- recovery.py
s = open(G + 'recovery_v49.py').read()
s = sub(s, "'Crooks E', 'Crooks F', 'Crooks G', 'Crooks H', 'Crooks I', 'Crooks J']",
        "'Crooks E', 'Crooks F', 'Crooks G', 'Crooks H', 'Crooks I', 'Crooks J', 'Crooks K', 'Crooks L']")
s = sub(s, "CFAM = ('Crooks C', 'Crooks E', 'Crooks F', 'Crooks G', 'Crooks H', 'Crooks I', 'Crooks J')",
        "CFAM = ('Crooks C', 'Crooks E', 'Crooks F', 'Crooks G', 'Crooks H', 'Crooks I', 'Crooks J', 'Crooks K', 'Crooks L')   # v5.0: + K, L")
s = sub(s, "LADFAM = ('Crooks F', 'Crooks G', 'Crooks H', 'Crooks I', 'Crooks J')",
        "LADFAM = ('Crooks F', 'Crooks G', 'Crooks H', 'Crooks I', 'Crooks J', 'Crooks K')   # v5.0: + K")
s = sub(s, "jX=20.0, lad=None, ladT=1000.0, baseMode='usd', basePct=1.0):",
        "jX=20.0, lad=None, ladT=1000.0, baseMode='usd', basePct=1.0,\n"
        "             sizeBy='risk', kMode='lots', kUsd=25.0, kPct=50.0, lZ1=2.0, lZ1N=6, lZ2=5.0, lZ2N=3, lGrow=10.0, lGrowX=4.0):")
s = sub(s, '''    fixed lots lose at that trade's stop); the rule sizes every trade from it, and a trade is booked with its own base (Oscar's Grind, Crooks G)."""''',
        '''    fixed lots lose at that trade's stop); the rule sizes every trade from it, and a trade is booked with its own base (Oscar's Grind, Crooks G).
    v5.0 (v50/SPEC_v50.md): sizeBy 'profit': the base (usd / pct) and every amount a rule adds are the WIN at the final TP: divided by exitR
    (D); Oscar's goal is one base win. Crooks K (Crooks J + ladder above the zero line; below it the careful size after a win: kMode 'lots'
    = the 8th element (the careful lots' $ risk), 'usd' = kUsd / D, 'pct' = kPct % of the base; after a loss the 0.01 lot). Crooks L (the
    0.01 lot while waiting; the parts of a loss set when it is booked: lZ1 / lZ1N below the start, lZ2 / lZ2N below the best; at a new best
    the base grows lGrow % of the profit / D, at most lGrowX x)."""''')
# state: L's N is 1; D
s = sub(s, "    crL = 0.0; crN = 0; crW = False      # Crooks: $ loss to win back, closed trades in the cycle, the last trade won (Crooks C)\n"
           "    crP = cN                             # Crooks C over N wins: parts of the loss still to win back (each recovery trade wins loss / parts)\n",
        "    crL = 0.0; crN = 0; crW = False      # Crooks: $ loss to win back, closed trades in the cycle, the last trade won (Crooks C)\n"
        "    cN = 1 if mode == 'Crooks L' else cN   # v5.0 Crooks L: its parts come from the drawdown (over N wins is not used)\n"
        "    crP = cN                             # Crooks C over N wins: parts of the loss still to win back (each recovery trade wins loss / parts)\n"
        "    pm = sizeBy == 'profit'; D = exitR if pm else 1.0   # v5.0 Size By profit\n")
# base
s = sub(s, "        b = base if baseMode == 'usd' else (max(0.0, eq) * basePct / 100.0 if baseMode == 'pct' else tr[6])   # v4.7: this trade's base ($ / % of equity / fixed lots' $, the 7th element)\n",
        "        b = base if baseMode == 'usd' else (max(0.0, eq) * basePct / 100.0 if baseMode == 'pct' else tr[6])   # v4.7: this trade's base ($ / % of equity / fixed lots' $, the 7th element)\n"
        "        if pm and baseMode != 'lot': b = b / exitR                       # v5.0: the base is the win at the final TP\n")
s = sub(s, "        add = recPool if mode == MODES[1] else recPool / recN if mode == MODES[2] else recPool * recPct / 100 if mode == MODES[3] else recPool / exitR if mode == MODES[5] else step * recLosses if mode == MODES[6] else 0.0\n",
        "        add = recPool / D if mode == MODES[1] else recPool / recN / D if mode == MODES[2] else recPool * recPct / 100 / D if mode == MODES[3] else recPool / exitR if mode == MODES[5] else step * recLosses / D if mode == MODES[6] else 0.0\n")
s = sub(s, "        baseC = max(b, min(stepBase, cap) if cap > 0 else stepBase) if mode == MODES[10] else b\n",
        "        stepBase = stepBase / D                                         # v5.0: a base amount\n"
        "        baseC = max(b, min(stepBase, cap) if cap > 0 else stepBase) if mode == MODES[10] else b\n")
s = sub(s, "        oscNeed = int(max(1, math.ceil((b - oscP) / (b * exitR))))\n",
        "        oscNeed = int(max(1, math.ceil(((b * exitR if pm else b) - oscP) / (b * exitR))))   # v5.0: with profit the goal is one base win\n")
s = sub(s, "             MODES[15]: (b + recPool / recN) if recLosses >= delayN else b, MODES[16]: eq * eqPct / 100.0, MODES[17]: b * min(oscU, oscNeed),",
        "             MODES[15]: (b + recPool / recN / D) if recLosses >= delayN else b, MODES[16]: eq * eqPct / 100.0 / D, MODES[17]: b * min(oscU, oscNeed),")
s = sub(s, "             MODES[9]: max(baseC, carried / cSplit), MODES[10]: max(baseC, carried / cSplit),",
        "             MODES[9]: max(baseC, carried / cSplit / D), MODES[10]: max(baseC, carried / cSplit / D),")
# Crooks: K / L
s = sub(s, "                    elif mode == 'Crooks J': x = max(B, x * max(0.0, 1.0 - (peakNet - net) / (jX * B)))   # = peak - equity, exact at any start\n"
           "                elif crL > 0 and mode in ('Crooks E', 'Crooks I') and rmin is not None: x = min(B, rmin)\n",
        "                    elif mode in ('Crooks J', 'Crooks K'): x = max(B, x * max(0.0, 1.0 - (peakNet - net) / (jX * B)))   # = peak - equity, exact at any start (v5.0: K too)\n"
        "                elif crL > 0 and mode in ('Crooks E', 'Crooks I', 'Crooks L') and rmin is not None: x = min(B, rmin)   # v5.0: L waits with the lot too\n")
s = sub(s, "            r = crk(b)\n"
           "            lon, lguard, lB, lC = lad_state(lad if mode in LADFAM else None, ladT, net, peakNet, b)\n"
           "            if lon:                                                  # v4.6 profit ladder\n"
           "                r = min(crk(lB), r + LADDER[lad][3] * lC)\n"
           "                if lguard: r = min(b, rmin) if rmin is not None else b\n",
        "            bL = b                                                    # v5.0 Crooks L: at a new best the base grows with the profit\n"
        "            if mode == 'Crooks L' and net >= peakNet: bL = b + min((max(1.0, lGrowX) - 1.0) * b, max(0.0, lGrow / 100.0 * net / D))\n"
        "            r = crk(bL)\n"
        "            lon, lguard, lB, lC = lad_state(lad if mode in LADFAM else None, ladT, net, peakNet, b)\n"
        "            if lon:                                                  # v4.6 profit ladder\n"
        "                r = min(crk(lB), r + LADDER[lad][3] * lC)\n"
        "                if lguard and mode != 'Crooks K': r = min(b, rmin) if rmin is not None else b   # v5.0: no start guard for K (its zone)\n"
        "            if mode == 'Crooks K' and net < 0:                        # v5.0 Crooks K below the zero line: careful after a win, else the lot\n"
        "                if crW:\n"
        "                    kr = tr[7] if len(tr) > 7 and tr[7] is not None and tr[7] > 0 else None\n"
        "                    r = (kUsd / D) if kMode == 'usd' else (b * kPct / 100.0) if kMode == 'pct' else (kr if kr is not None else b)\n"
        "                else: r = min(b, rmin) if rmin is not None else b\n")
# hard cap reset, cycle reset: cN is already 1 for L (assigned above)
# Oscar booking
s = sub(s, "        if oscP >= b: oscU = 1; oscP = 0.0\n",
        "        if oscP >= (b * exitR if pm else b): oscU = 1; oscP = 0.0        # v5.0: with profit the goal is one base win\n")
# L parts at a booked loss
s = sub(s, "            crP = cN if not win else (max(1, crP - 1) if crRec else crP)     # a loss starts the N parts again after the next win\n",
        "            crP = (lparts(b) if mode == 'Crooks L' else cN) if not win else (max(1, crP - 1) if crRec else crP)     # a loss starts the N parts again after the next win (v5.0 L: from the drawdown)\n")
s = sub(s, "    for k, tr in enumerate(trades):\n        res, c = tr[0], tr[1]; parts = tr[2] if len(tr) > 2 else None\n",
        "    def lparts(bb):                      # v5.0 Crooks L: the parts of the loss just booked (net / peakNet after it)\n"
        "        if net < 0: dd, st_, mx = -net, lZ1 * bb, max(1, lZ1N)\n"
        "        elif net < peakNet: dd, st_, mx = peakNet - net, lZ2 * bb, max(1, lZ2N)\n"
        "        else: return 1\n"
        "        return int(max(1, min(mx, math.ceil(dd / st_ - 1e-9)))) if st_ > 0 else 1\n"
        "    for k, tr in enumerate(trades):\n        res, c = tr[0], tr[1]; parts = tr[2] if len(tr) > 2 else None\n")
open(G + 'recovery.py', 'w').write(s)

# ---------------------------------------------------------------- crooks_tp1.py
t = open(G + 'crooks_tp1_v49.py').read()
t = sub(t, "CFAM = ('Crooks C', 'Crooks E', 'Crooks F', 'Crooks G', 'Crooks H', 'Crooks I', 'Crooks J')   # v4.5: Crooks C and the rules built on it",
        "CFAM = ('Crooks C', 'Crooks E', 'Crooks F', 'Crooks G', 'Crooks H', 'Crooks I', 'Crooks J', 'Crooks K', 'Crooks L')   # v4.5: Crooks C and the rules built on it (v5.0: K, L)")
t = sub(t, "             fK=3.0, gX=10.0, hPct=1.0, jX=20.0, lad=None, ladT=1000.0):",
        "             fK=3.0, gX=10.0, hPct=1.0, jX=20.0, lad=None, ladT=1000.0, sizeBy='risk', kMode='lots', kUsd=25.0, kPct=50.0,\n"
        "             lZ1=2.0, lZ1N=6, lZ2=5.0, lZ2N=3, lGrow=10.0, lGrowX=4.0):")
t = sub(t, '''    is at or below 0 (the start guard) the trade is the 0.01 lot without the TP1 rule."""''',
        '''    is at or below 0 (the start guard) the trade is the 0.01 lot without the TP1 rule.
    v5.0 (v50/SPEC_v50.md): sizeBy 'profit' (base / exitR), Crooks K (no TP1 rule below the zero line; x['krisk'] = the careful lots' $ risk),
    Crooks L (the 0.01 lot while waiting, the parts of a loss from the drawdown when it is booked, base growth at a new best)."""''')
t = sub(t, "    crL = 0.0; crN = 0; crW = False; crP = cN; busy = -1;",
        "    cN = 1 if mode == 'Crooks L' else cN; pm = sizeBy == 'profit'; D = exitR if pm else 1.0; b = base / exitR if pm else base   # v5.0\n"
        "    def lparts(bb):\n"
        "        if net < 0: dd, st_, mx = -net, lZ1 * bb, max(1, lZ1N)\n"
        "        elif net < peakNet: dd, st_, mx = peakNet - net, lZ2 * bb, max(1, lZ2N)\n"
        "        else: return 1\n"
        "        return int(max(1, min(mx, math.ceil(dd / st_ - 1e-9)))) if st_ > 0 else 1\n"
        "    crL = 0.0; crN = 0; crW = False; crP = cN; busy = -1;")
t = sub(t, "        lon, lguard, lB, lC = RC.lad_state(lad if mode in RC.LADFAM else None, ladT, net, peakNet, base)   # v4.6 profit ladder\n"
           "        sp = rec and tp1rule and x['sp'] is not None and not lguard\n",
        "        lon, lguard, lB, lC = RC.lad_state(lad if mode in RC.LADFAM else None, ladT, net, peakNet, b)   # v4.6 profit ladder\n"
        "        if mode == 'Crooks K': lguard = False                       # v5.0: K has no start guard ...\n"
        "        kz = mode == 'Crooks K' and net < 0                         # ... but its zone below the zero line (no TP1 rule there)\n"
        "        sp = rec and tp1rule and x['sp'] is not None and not lguard and not kz\n")
t = sub(t, "                elif mode == 'Crooks J': q = max(B, q * max(0.0, 1.0 - max(0.0, peakNet - net) / (jX * B)))\n"
           "            elif cfam and crL > 0 and mode in ('Crooks E', 'Crooks I') and x.get('rmin') is not None: q = min(B, x['rmin'])   # v4.5 Crooks E / I\n",
        "                elif mode in ('Crooks J', 'Crooks K'): q = max(B, q * max(0.0, 1.0 - max(0.0, peakNet - net) / (jX * B)))\n"
        "            elif cfam and crL > 0 and mode in ('Crooks E', 'Crooks I', 'Crooks L') and x.get('rmin') is not None: q = min(B, x['rmin'])   # v4.5 Crooks E / I (v5.0: L)\n")
t = sub(t, "        r = crk(base)\n"
           "        if lon: r = min(base, x['rmin']) if lguard else min(crk(lB), r + RC.LADDER[lad][3] * lC / m)\n",
        "        bL = b + min((max(1.0, lGrowX) - 1.0) * b, max(0.0, lGrow / 100.0 * net / D)) if (mode == 'Crooks L' and net >= peakNet) else b\n"
        "        r = crk(bL)\n"
        "        if lon: r = min(b, x['rmin']) if lguard else min(crk(lB), r + RC.LADDER[lad][3] * lC / m)\n"
        "        if kz: r = ((kUsd / D) if kMode == 'usd' else (b * kPct / 100.0) if kMode == 'pct' else x.get('krisk', b)) if crW else min(b, x['rmin'])\n")
t = sub(t, "            elif capAction == 'reset': crL = 0.0; crN = 0; crW = False; crP = cN; rec = sp = False; r = min(base, cap)\n",
        "            elif capAction == 'reset': crL = 0.0; crN = 0; crW = False; crP = cN; rec = sp = False; r = min(b, cap)\n")
t = sub(t, "        if mode == 'Crooks G': crL = min(crL, gX * RC.lad_state(lad if mode in RC.LADFAM else None, ladT, net, peakNet, base)[2])   # v4.5 (v4.6: the ladder base)\n",
        "        if mode == 'Crooks G': crL = min(crL, gX * RC.lad_state(lad if mode in RC.LADFAM else None, ladT, net, peakNet, b)[2])   # v4.5 (v4.6: the ladder base)\n")
t = sub(t, "            crP = cN if not win else (max(1, crP - 1) if rec else crP)\n",
        "            crP = (lparts(b) if mode == 'Crooks L' else cN) if not win else (max(1, crP - 1) if rec else crP)\n")
open(G + 'crooks_tp1.py', 'w').write(t)
print('recovery.py and crooks_tp1.py v5.0 written')
