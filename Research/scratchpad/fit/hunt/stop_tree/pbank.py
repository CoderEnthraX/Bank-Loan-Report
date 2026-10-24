"""Previous-session / overnight-gap feature bank (stop_tree phase 2).  pfeats(P, i, d) -> dict.
Session definitions (prefix): R = VWAP reset (= TradingView 'D' bar of the symbol), M = R with <24-bar stubs merged into the
next session, U = UTC calendar day, I = IST calendar day, Um/Im = U/I with <24-bar stubs merged.
All directional features are d-normalised (positive = in the trade direction).  A = ATR14 (RMA) at the arm bar."""
import sys, os, math, pickle, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fbase import FIT, base, sigs
sys.path.insert(0, FIT)
NAN = float('nan')


def sess_def(P, name):
    key = ('pb_sess', name)
    if key in P: return P[key]
    T = P['T']; n = len(T)
    if name in ('R', 'M'):
        st = [i for i, x in enumerate(P['daystart']) if x]
    else:
        if name.startswith('U'):
            day = [(dt.datetime.strptime(t, '%Y-%m-%d %H:%M') - dt.timedelta(hours=5, minutes=30)).date() for t in T]
        else:
            day = [t[:10] for t in T]
        st = [0] + [i for i in range(1, n) if day[i] != day[i - 1]]
    st = st + [n]
    merge = name in ('M', 'Um', 'Im')
    out = []; carry = None
    for a, b in zip(st[:-1], st[1:]):
        if carry is not None: a, carry = carry, None
        if merge and b - a < 24 and b < n: carry = a; continue
        out.append((a, b))
    idx = [0] * n
    for k, (a, b) in enumerate(out):
        for i in range(a, b): idx[i] = k
    P[key] = (out, idx); return P[key]


def svwap(P, a, b):
    vol = P['vol']; H, L, C = P['H'], P['L'], P['C']; s = w = 0.0
    for j in range(a, b):
        v = vol[j] or 0.0; s += v * (H[j] + L[j] + C[j]) / 3; w += v
    return s / w if w > 0 else (H[b - 1] + L[b - 1] + C[b - 1]) / 3


def eng_trades(P):
    if 'pb_eng' in P: return P['pb_eng']
    from engine2 import run
    BEST = {"brkLen": 10, "entryLen": 6, "bodyPct": 55, "closePct": 25, "maxDayR": 3, "vsLag": 3, "noSunUTC": 1, "momMin": 0.85,
            "roundLevels": False, "rearm": "samedir", "minBars": 1}
    P['pb_eng'] = run(P, BEST); return P['pb_eng']


def pfeats(P, i, d, defs=('R', 'M', 'U', 'I', 'Um', 'Im')):
    O, H, L, C, V = P['O'], P['H'], P['L'], P['C'], P['V']; A = P[('atr', 14)][i]; f = {}
    E = eng_trades(P)
    for sd in defs:
        S, idx = sess_def(P, sd); k = idx[i]; a = S[k][0]
        g = lambda nm, v: f.__setitem__(f'{sd}_{nm}', v)
        g('cSince', i - a)
        # current session so far
        so = O[a]; shx = max(H[a:i]) if i > a else H[i]; slx = min(L[a:i]) if i > a else L[i]
        cfav = shx if d > 0 else slx; cadv = slx if d > 0 else shx
        g('cMoveA', d * (C[i] - so) / A); g('cRngA', (max(shx, H[i]) - min(slx, L[i])) / A)
        g('cFavExA', d * (C[i] - cfav) / A); g('cAdvExA', d * (C[i] - cadv) / A)
        g('cOpenAdvA', d * (so - cadv) / A)
        if k < 1:
            continue
        pa, pb = S[k - 1]; po, pc = O[pa], C[pb - 1]; ph, pl = max(H[pa:pb]), min(L[pa:pb]); pr = ph - pl or 1e-12
        pfav = ph if d > 0 else pl; padv = pl if d > 0 else ph
        pvw = V[pb - 1] if V[pb - 1] is not None else svwap(P, pa, pb); psv = svwap(P, pa, pb)
        rngs = [max(H[x:y]) - min(L[x:y]) for x, y in S[max(0, k - 5):k]]; Ad = sum(rngs) / len(rngs)
        loc = lambda x: ((x - pl) / pr) if d > 0 else ((ph - x) / pr)
        g('pLen', pb - pa)
        g('pBodyA', d * (pc - po) / A); g('pBodyF', d * (pc - po) / pr); g('pBodyD', d * (pc - po) / Ad); g('pBodyPct', d * (pc - po) / po * 100)
        g('pRngA', pr / A); g('pRngD', pr / Ad); g('AdA', Ad / A)
        g('pCloc', loc(pc)); g('pOloc', loc(po)); g('pMidA', d * (pc - (ph + pl) / 2) / A)
        g('pCvwA', d * (pc - pvw) / A); g('pCvwF', d * (pc - pvw) / pr); g('pCsvA', d * (pc - psv) / A)
        g('pOvwA', d * (po - pvw) / A)
        g('pFavOA', d * (pfav - po) / A); g('pAdvOA', d * (po - padv) / A)
        g('pFavWickA', d * (pfav - (max(po, pc) if d > 0 else min(po, pc))) / A)
        g('pAdvWickA', d * ((min(po, pc) if d > 0 else max(po, pc)) - padv) / A)
        for N in (6, 12, 24, 48):
            g(f'pLast{N}A', d * (pc - C[max(pa, pb - 1 - N)]) / A)
        mid = (pa + pb) // 2
        g('p1HalfA', d * (C[mid] - po) / A); g('p2HalfA', d * (pc - C[mid]) / A)
        jf = max(range(pa, pb), key=lambda j: d * (H[j] if d > 0 else -L[j]) * (1 if d > 0 else 1)) if d > 0 else min(range(pa, pb), key=lambda j: L[j])
        ja = min(range(pa, pb), key=lambda j: L[j]) if d > 0 else max(range(pa, pb), key=lambda j: H[j])
        g('pAdvLast', 1.0 if ja > jf else 0.0)
        g('pFavPos', (jf - pa) / (pb - pa)); g('pAdvPos', (ja - pa) / (pb - pa))
        vfirst = V[pa] if V[pa] is not None else pvw
        g('pVwDriftA', d * (pvw - vfirst) / A)
        g('pAboveVw', sum(1 for j in range(pa, pb) if V[j] is not None and d * (C[j] - V[j]) > 0) / (pb - pa))
        g('pUpBars', sum(1 for j in range(pa, pb) if d * (C[j] - O[j]) > 0) / (pb - pa))
        for nm in ('core', 'vsl', 'full', 'arm'):
            sg = sigs(P, nm); ps = [x for x in sg[pa:pb] if x]
            g(f'pE{nm}Net', d * sum(ps)); g(f'pE{nm}Same', sum(1 for x in ps if x == d)); g(f'pE{nm}Opp', sum(1 for x in ps if x == -d))
            g(f'pE{nm}First', d * ps[0] if ps else 0); g(f'pE{nm}Last', d * ps[-1] if ps else 0)
            g(f'pE{nm}Frac', d * sum(ps) / len(ps) if ps else 0.0)
        # overnight gap / current vs previous session
        g('gapA', d * (so - pc) / A); g('gapD', d * (so - pc) / Ad); g('gapVwA', d * (so - pvw) / A)
        g('openFavA', d * (so - pfav) / A); g('openAdvA', d * (so - padv) / A); g('openLoc', loc(so))
        g('cVsPcA', d * (C[i] - pc) / A); g('cVsPoA', d * (C[i] - po) / A); g('cVsPfavA', d * (C[i] - pfav) / A)
        g('cVsPadvA', d * (C[i] - padv) / A); g('cVsPvwA', d * (C[i] - pvw) / A); g('cLocP', loc(C[i]))
        g('cBeyondPadv', 1.0 if d * (cadv - padv) < 0 else 0.0); g('cBeyondPfav', 1.0 if d * (cfav - pfav) > 0 else 0.0)
        # engine trades
        inprev = [m for m in E if pa <= m['fill'] < pb]
        g('eNP', len(inprev)); g('eRP', sum(m['res'] or 0 for m in E if m['exit'] is not None and pa <= m['exit'] < pb))
        before = [m for m in E if m['fill'] < a]
        if before:
            m = before[-1]; g('eLastD', m['dir'] * d); g('eLastR', m['res'] if m['res'] is not None else 0.0)
            g('eLastSD', (m['res'] or 0) * m['dir'] * d)
            g('eOpenAtStart', 1.0 if (m['exit'] is None or m['exit'] >= a) else 0.0)
        else:
            g('eLastD', 0.0); g('eLastR', 0.0); g('eLastSD', 0.0); g('eOpenAtStart', 0.0)
        if k < 2:
            continue
        qa, qb = S[k - 2]; qo, qc = O[qa], C[qb - 1]; qh, ql = max(H[qa:qb]), min(L[qa:qb]); qr = qh - ql or 1e-12
        g('pCCA', d * (pc - qc) / A); g('pCCD', d * (pc - qc) / Ad); g('pCCPct', d * (pc - qc) / qc * 100)
        g('p2BodyA', d * (qc - qo) / A); g('p2BodyF', d * (qc - qo) / qr); g('p2RngA', qr / A)
        g('p2Cloc', ((qc - ql) / qr) if d > 0 else ((qh - qc) / qr))
        g('sum2BodyA', d * (pc - qo) / A); g('sum2BodyF', d * (pc - qo) / (max(ph, qh) - min(pl, ql)))
        g('p2GapA', d * (po - qc) / A)
        g('pInsideP2', 1.0 if ph <= qh and pl >= ql else 0.0)
        g('pVsP2favA', d * (pc - (qh if d > 0 else ql)) / A); g('pVsP2advA', d * (pc - (ql if d > 0 else qh)) / A)
        g('cVsP2cA', d * (C[i] - qc) / A)
        q2v = V[qb - 1] if V[qb - 1] is not None else svwap(P, qa, qb)
        g('p2CvwA', d * (qc - q2v) / A); g('pVwVsP2vwA', d * (pvw - q2v) / A)
        sg = sigs(P, 'vsl'); g('pEvslNet2', d * sum(sg[qa:pb]))
        nag = [1 if d * (pc - po) < 0 else 0, 1 if d * (qc - qo) < 0 else 0]
        g('nAg2', sum(nag))
        if k >= 3:
            ra, rb = S[k - 3]; g('p3BodyA', d * (C[rb - 1] - O[ra]) / A); g('nAg3', sum(nag) + (1 if d * (C[rb - 1] - O[ra]) < 0 else 0))
            g('sum3BodyA', d * (pc - O[ra]) / A)
    return f


if __name__ == '__main__':
    from tightdata import TRADES
    from subset import first_flag
    out = []
    for t in TRADES:
        P = base(t['sym'])
        f = pfeats(P, t['arm_i'], t['d'])
        for m in (True, False):
            for nm, ex in (('vsl', ('vsl',)), ('core', ()), ('full', ('vw', 'mom', 'vsl'))):
                f[f'first_{nm}_{"M" if m else "R"}'] = 1.0 if first_flag(P, t['arm_i'], t['d'], m, ex) else 0.0
        out.append((t, f))
    pickle.dump(out, open(os.path.join(HERE, 'pbank.pkl'), 'wb'))
    keys = sorted(set(k for _, f in out for k in f))
    print(len(out), 'trades', len(keys), 'features')
