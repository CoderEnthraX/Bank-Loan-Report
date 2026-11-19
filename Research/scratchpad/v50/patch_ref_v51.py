"""v5.1 reference (SPEC section 5): with Size By profit every amount-to-risk conversion uses the setup's D = the win per $ of stop-out loss at
the final TP (trade element [8] in recovery.py, x['pd'] in crooks_tp1.py; absent: exitR = v5.0). Applied to the v5.0 copies (*_v50.py).
Risk mode unchanged (checked by v50/ref_regress51.py)."""
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
G = S + '/gold/'


def sub(s, a, b, n=1):
    assert s.count(a) == n, (a[:100], s.count(a))
    return s.replace(a, b)


s = open(G + 'recovery_v50.py').read()
s = sub(s, "    pm = sizeBy == 'profit'; D = exitR if pm else 1.0   # v5.0 Size By profit\n",
        "    pm = sizeBy == 'profit'                # v5.0 Size By profit (v5.1: D per trade, below)\n")
s = sub(s, "        if pm and baseMode != 'lot': b = b / exitR                       # v5.0: the base is the win at the final TP\n",
        "        Dt = (tr[8] if len(tr) > 8 and tr[8] is not None else exitR) if pm else exitR   # v5.1: a final-TP win per $ of stop-out loss (this setup)\n"
        "        D = Dt if pm else 1.0; XR = Dt if pm else exitR                  # amounts / D; Exact and the Crooks recovery / XR (Risk: exitR)\n"
        "        if pm and baseMode != 'lot': b = b / D                           # v5.0: the base is the win at the final TP\n")
s = sub(s, "recPool * recPct / 100 / D if mode == MODES[3] else recPool / exitR if mode == MODES[5] else",
        "recPool * recPct / 100 / D if mode == MODES[3] else recPool / XR if mode == MODES[5] else")
s = sub(s, "        oscNeed = int(max(1, math.ceil(((b * exitR if pm else b) - oscP) / (b * exitR))))   # v5.0: with profit the goal is one base win\n",
        "        oscNeed = int(max(1, math.ceil(((b * D if pm else b) - oscP) / (b * XR))))   # v5.0: with profit the goal is one base win (v5.1: x D)\n")
s = sub(s, "             MODES[18]: max(b, crL / exitR) if crRec else b, MODES[19]: max(b, crL / cSplit / exitR) if crRec else b,\n"
           "             MODES[20]: max(b, crL / crP * (crkPrPct / 100.0 if prOn and crkPr == 'pct' else 1.0) / exitR) if crRec else b,\n"
           "             MODES[21]: max(b, crL / exitR) if crRec else b}.get(mode, b + add)\n",
        "             MODES[18]: max(b, crL / XR) if crRec else b, MODES[19]: max(b, crL / cSplit / XR) if crRec else b,\n"
        "             MODES[20]: max(b, crL / crP * (crkPrPct / 100.0 if prOn and crkPr == 'pct' else 1.0) / XR) if crRec else b,\n"
        "             MODES[21]: max(b, crL / XR) if crRec else b}.get(mode, b + add)\n")
s = sub(s, "                x = max(B, crL / crP * (crkPrPct / 100.0 if prOn and crkPr == 'pct' else 1.0) / exitR) if crRec else B\n",
        "                x = max(B, crL / crP * (crkPrPct / 100.0 if prOn and crkPr == 'pct' else 1.0) / XR) if crRec else B\n")
s = sub(s, "        if oscP >= (b * exitR if pm else b): oscU = 1; oscP = 0.0        # v5.0: with profit the goal is one base win\n",
        "        if oscP >= (b * D if pm else b): oscU = 1; oscP = 0.0            # v5.0: with profit the goal is one base win (v5.1: x D)\n")
s = sub(s, "the base grows lGrow % of the profit / D, at most lGrowX x).\"\"\"",
        "the base grows lGrow % of the profit / D, at most lGrowX x).\n"
        "    v5.1: with profit D = the 9th element of the trade (a final-TP win per $ of stop-out loss on that setup, costs included; absent: exitR),\n"
        "    used for every amount (also Exact and the Crooks recovery, which divide by exitR in Risk mode).\"\"\"")
open(G + 'recovery.py', 'w').write(s)

t = open(G + 'crooks_tp1_v50.py').read()
t = sub(t, "    cN = 1 if mode == 'Crooks L' else cN; pm = sizeBy == 'profit'; D = exitR if pm else 1.0; b = base / exitR if pm else base   # v5.0\n",
        "    cN = 1 if mode == 'Crooks L' else cN; pm = sizeBy == 'profit'   # v5.0 (v5.1: D and the base per trade, below)\n")
t = sub(t, "    for k, x in enumerate(tr):\n",
        "    for k, x in enumerate(tr):\n"
        "        Dt = x.get('pd', exitR) if pm else exitR; D = Dt if pm else 1.0; XR = Dt if pm else exitR; b = base / D if pm else base   # v5.1\n")
t = sub(t, "            q = max(B, X) if sp else max(B, X / exitR) if rec else B\n",
        "            q = max(B, X) if sp else max(B, X / XR) if rec else B\n")
t = sub(t, "    v5.0 (v50/SPEC_v50.md): sizeBy 'profit' (base / exitR),",
        "    v5.1: sizeBy 'profit' divides by x['pd'] (a final-TP win per $ of stop-out loss of that trade; absent: exitR).\n"
        "    v5.0 (v50/SPEC_v50.md): sizeBy 'profit' (base / exitR),")
open(G + 'crooks_tp1.py', 'w').write(t)
print('reference v5.1 written')
