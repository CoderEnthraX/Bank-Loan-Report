LEVELS = {'Off': None, 'Low': (0.8,0.10,2,0.25), 'Medium': (0.7,0.15,3,0.30),
          'High': (0.6,0.20,5,0.35), 'Extra high': (0.5,0.25,8,0.40), 'Max': (0.4,0.30,12,0.50)}
LVL_ORDER = ['Off','Low','Medium','High','Extra high','Max']
# setting list in column order E..AJ
SETTINGS = [('NOREC', None), ('E', None)]
for rule in 'FGHIJ':
    for lv in LVL_ORDER:
        SETTINGS.append((rule, lv))
assert len(SETTINGS) == 32

def run(trades, rule, level, start=10000.0, b=50.0, T=1000.0):
    """returns list of (trade, pnl)"""
    exitR_unused = None
    eq = start; net = 0.0; peak = 0.0; crL = 0.0; crW = False; ruined = False
    lad = LEVELS.get(level) if level else None
    out = []
    mult = {'F': 3, 'I': 3}
    for t in trades:
        if ruined:
            out.append(0.0); continue
        R = t['R']; c = t['c']; rp = t['rp']; lim = t['lim']
        levk = 100 * (rp + 0.23) / lim
        rmin = rp + 0.23
        def plain(B):
            recovery = crW and crL > 0
            if recovery:
                x = max(B, crL / t['_exitR'])
                if rule in ('F', 'I'): x = min(x, 3 * B)
                elif rule == 'H': x = min(x, max(B, 0.01 * eq))
                elif rule == 'J': x = max(B, x * max(0.0, 1 - (peak - net) / (20 * B)))
                return x
            elif crL > 0 and rule in ('E', 'I'):
                return min(B, rmin)
            return B
        if rule == 'NOREC':
            r = b
        else:
            r = plain(b)
            if lad is not None and rule != 'E' and peak >= T:
                lam, phi, bmax, gam = lad
                C = max(0.0, net - lam * peak)
                B = b + min((bmax - 1) * b, phi * C)
                r = min(plain(B), r + gam * C)
                if net <= 0:
                    r = min(b, rmin)
        if eq > 0:
            r = min(r, eq * levk)
        pnl = r * (R - c) / (1 + c)
        eq += pnl; net += pnl; peak = max(peak, net)
        if eq <= 0: ruined = True
        crL = max(0.0, crL - pnl)
        if rule == 'G':
            if lad is not None and peak >= T:
                lam, phi, bmax, gam = lad
                B2 = b + min((bmax - 1) * b, phi * max(0.0, net - lam * peak))
            else:
                B2 = b
            crL = min(crL, 10 * B2)
        if crL < 0.01: crL = 0.0
        crW = pnl > 0
        out.append(pnl)
    return out
