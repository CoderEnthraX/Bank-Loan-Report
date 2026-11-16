"""ref_gbe.py = gold/ref_g.py (the research engine) + BE trigger and salvage trigger in R (asked 2026-11-16), decided at the candle close like
every engine rule (the indicator, strategy and EA would copy it), acting from the next candle:
  BE trigger      beOn / beR: a candle (after the fill candle, the trade still open) reaches entry + beR x risk -> the stop moves to the entry
  salvage trigger svOn / svR: a candle reaches entry - svR x risk -> the final target moves to the entry (out at 0R if the price comes back)
Only the first of the two acts in a trade (both on one candle: the extreme nearer the open came first). A target exit at the moved target is
0R. The fill candle never triggers (the engine takes no target on it either). Off = ref_g exactly."""
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
s = open(S + '/gold/ref_g.py').read()


def sub1(a, b):
    global s
    assert s.count(a) == 1, (a[:80], s.count(a))
    s = s.replace(a, b)


sub1("    kzOn=False, kz=(True, True, True, True), kzShift=0, kzAuto=False)",
     "    kzOn=False, kz=(True, True, True, True), kzShift=0, kzAuto=False, beOn=False, beR=0.3, svOn=False, svR=0.5)")
sub1("""                res = exitR if win else (-1.0 if stp == stp0 else d * (stp - lim) / trRisk)""",
     """                res = (exitR if not svAct else d * (tF - lim) / trRisk) if win else (-1.0 if stp == stp0 else d * (stp - lim) / trRisk)""")
sub1("""                lastExit = i; st = 0; cur.update(exit=i, res=res, best=bestPx, stpX=stp)
            elif reached > prevHit:
                ns = stp
                if p['mv1On'] and reached >= 1: ns = max(ns, lim + p['mv1R'] * trRisk) if isL else min(ns, lim - p['mv1R'] * trRisk)
                if p['mv2On'] and reached >= 2: ns = max(ns, lim + p['mv2R'] * trRisk) if isL else min(ns, lim - p['mv2R'] * trRisk)
                if p['mv3On'] and reached >= 3: ns = max(ns, lim + p['mv3R'] * trRisk) if isL else min(ns, lim - p['mv3R'] * trRisk)
                stp = ns
""", """                lastExit = i; st = 0; cur.update(exit=i, res=res, best=bestPx, stpX=stp, trig=trig)
            else:
                if reached > prevHit:
                    ns = stp
                    if p['mv1On'] and reached >= 1: ns = max(ns, lim + p['mv1R'] * trRisk) if isL else min(ns, lim - p['mv1R'] * trRisk)
                    if p['mv2On'] and reached >= 2: ns = max(ns, lim + p['mv2R'] * trRisk) if isL else min(ns, lim - p['mv2R'] * trRisk)
                    if p['mv3On'] and reached >= 3: ns = max(ns, lim + p['mv3R'] * trRisk) if isL else min(ns, lim - p['mv3R'] * trRisk)
                    stp = ns
                if trig is None and (p['beOn'] or p['svOn']):     # BE / salvage trigger (from the next candle)
                    beL = lim + d * p['beR'] * trRisk; svL = lim - d * p['svR'] * trRisk
                    beH = p['beOn'] and (H[i] >= beL - mt * 0.001 if isL else L[i] <= beL + mt * 0.001)
                    svH = p['svOn'] and (L[i] <= svL + mt * 0.001 if isL else H[i] >= svL - mt * 0.001)
                    if beH and svH:                                # both on one candle: the extreme nearer the open came first
                        hiFirst = abs(H[i] - O[i]) < abs(O[i] - L[i])
                        if hiFirst == isL: svH = False
                        else: beH = False
                    if beH:
                        stp = max(stp, lim) if isL else min(stp, lim); trig = 'be'
                    elif svH:
                        tF = lim; svAct = True; trig = 'sv'
""")
sub1("                st = 2 if isL else -2; fillBar = i; lastFill = i; lastDir = d; tpHit = 0; dayFills += 1\n",
     "                st = 2 if isL else -2; fillBar = i; lastFill = i; lastDir = d; tpHit = 0; dayFills += 1; trig = None; svAct = False\n")
sub1("    lim = stp = stp0 = trRisk = None; t = [None] * 4; tF = None; tpHit = 0;",
     "    trig = None; svAct = False\n    lim = stp = stp0 = trRisk = None; t = [None] * 4; tF = None; tpHit = 0;")
open(S + '/bese/ref_gbe.py', 'w').write(s)
print('ref_gbe.py written')
